from datetime import date

from fastapi import FastAPI, Depends, Request, Form
from fastapi.responses import RedirectResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.status import HTTP_303_SEE_OTHER

from .database import Base, engine, SessionLocal
from . import crud, schemas, auth
from .camera_service import camera_service
from .barcode_service import detect_barcode
from .ocr_service import extract_expiry_date
from .product_lookup import lookup_product_by_barcode
from .led_service import led_service
from .expiry_service import expiry_status, expiry_label
from .analytics_service import build_dashboard_stats, build_analytics
from .recipe_service import build_recipe_suggestions


Base.metadata.create_all(bind=engine)

app = FastAPI(title="ExpireIQ")

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


# Creates a database session for each request, then closes it safely afterwards.
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def require_user(request: Request, db: Session):
    return auth.get_current_user(request, db)


def product_to_dict(product):
    return {
        "barcode": product.barcode,
        "name": product.name or "",
        "brand": product.brand or "",
        "size": product.size or "",
        "category": product.category or "",
        "full_category": product.full_category or ""
    }


def detect_barcode_with_retries(attempts=5):
    for _ in range(attempts):
        frame = camera_service.capture_image()
        barcode = detect_barcode(frame)

        if barcode:
            return barcode

    return None


def scan_type_label(scan_type):
    if scan_type == "barcode":
        return "Barcode Scan"

    if scan_type == "expiry_ocr":
        return "Expiry OCR"

    return scan_type.replace("_", " ").title()


templates.env.globals["scan_type_label"] = scan_type_label
templates.env.globals["expiry_status"] = expiry_status
templates.env.globals["expiry_label"] = expiry_label


# Page routes: render the main website screens.
@app.get("/")
def root(request: Request, db: Session = Depends(get_db)):
    user_id = auth.get_user_id_from_cookie(request)

    if user_id is None:
        return RedirectResponse("/login", status_code=HTTP_303_SEE_OTHER)

    return RedirectResponse("/dashboard", status_code=HTTP_303_SEE_OTHER)


@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(
        request,
        "register.html",
        {"error": None}
    )


@app.post("/register")
def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    existing_user = crud.get_user_by_username(db, username)

    if existing_user:
        return templates.TemplateResponse(
            request,
            "register.html",
            {"error": "Username already exists"}
        )

    password_hash = auth.hash_password(password)
    user = crud.create_user(db, username, password_hash)

    response = RedirectResponse("/dashboard", status_code=HTTP_303_SEE_OTHER)
    response.set_cookie("session", auth.create_session_cookie(user.id), httponly=True)

    return response


@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        request,
        "login.html",
        {"error": None}
    )


@app.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_username(db, username)

    if user is None or not auth.verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            request,
            "login.html",
            {"error": "Invalid username or password"}
        )

    response = RedirectResponse("/dashboard", status_code=HTTP_303_SEE_OTHER)
    response.set_cookie("session", auth.create_session_cookie(user.id), httponly=True)

    return response


@app.get("/logout")
def logout():
    response = RedirectResponse("/login", status_code=HTTP_303_SEE_OTHER)
    response.delete_cookie("session")

    return response


@app.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db)):
    user = require_user(request, db)
    items = crud.get_user_inventory(db, user.id)
    shopping_items = crud.get_shopping_list(db, user.id)
    stats = build_dashboard_stats(items)

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "user": user,
            "items": items,
            "shopping_items": shopping_items,
            "stats": stats
        }
    )


@app.get("/items")
def items_page(
    request: Request,
    search: str = "",
    category: str = "",
    sort: str = "expiry",
    db: Session = Depends(get_db)
):
    user = require_user(request, db)

    items = crud.get_user_inventory(db, user.id)
    categories = crud.get_inventory_categories(db, user.id)

    if search:
        search_lower = search.lower()

        items = [
            item for item in items
            if (
                search_lower in (item.product.name or "").lower()
                or search_lower in (item.product.brand or "").lower()
                or search_lower in (item.product.category or "").lower()
                or search_lower in (item.product.size or "").lower()
            )
        ]

    if category:
        items = [
            item for item in items
            if item.product.category == category
        ]

    if sort == "name":
        items.sort(key=lambda item: item.product.name or "")

    elif sort == "quantity":
        items.sort(key=lambda item: item.quantity, reverse=True)

    else:
        items.sort(
            key=lambda item: (
                item.expiration_date is None,
                item.expiration_date
            )
        )

    return templates.TemplateResponse(
        request,
        "items.html",
        {
            "user": user,
            "items": items,
            "categories": categories,
            "search": search,
            "selected_category": category,
            "sort": sort
        }
    )


@app.get("/items/{item_id}/edit")
def edit_item_page(
    item_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    user = require_user(request, db)
    item = crud.get_inventory_item(db, user.id, item_id)

    if item is None:
        return RedirectResponse("/items", status_code=HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        request,
        "edit_item.html",
        {
            "user": user,
            "item": item
        }
    )


@app.post("/items/{item_id}/edit")
def edit_item(
    item_id: int,
    request: Request,
    quantity: int = Form(...),
    expiration_date: str = Form(None),
    action: str = Form("save"),
    db: Session = Depends(get_db)
):
    user = require_user(request, db)

    if action == "delete":
        crud.delete_inventory_item(db, user.id, item_id)
        return RedirectResponse("/items", status_code=HTTP_303_SEE_OTHER)

    if action == "shopping":
        crud.add_inventory_item_to_shopping_list(db, user.id, item_id)
        return RedirectResponse("/shopping-list", status_code=HTTP_303_SEE_OTHER)

    expiry = date.fromisoformat(expiration_date) if expiration_date else None

    if quantity <= 0:
        crud.delete_inventory_item(db, user.id, item_id)
    else:
        crud.update_inventory_item(
            db=db,
            user_id=user.id,
            item_id=item_id,
            quantity=quantity,
            expiration_date=expiry
        )

    return RedirectResponse("/items", status_code=HTTP_303_SEE_OTHER)


@app.get("/shopping-list")
def shopping_list_page(request: Request, db: Session = Depends(get_db)):
    user = require_user(request, db)
    shopping_items = crud.get_shopping_list(db, user.id)

    return templates.TemplateResponse(
        request,
        "shopping_list.html",
        {
            "user": user,
            "shopping_items": shopping_items
        }
    )


@app.post("/shopping-list/add")
def add_shopping_item(
    request: Request,
    name: str = Form(...),
    quantity: int = Form(1),
    category: str = Form(None),
    db: Session = Depends(get_db)
):
    user = require_user(request, db)
    crud.create_shopping_item(
        db,
        user.id,
        name=name,
        quantity=quantity,
        category=category
    )

    return RedirectResponse("/shopping-list", status_code=HTTP_303_SEE_OTHER)


@app.post("/shopping-list/{shopping_item_id}/update")
def update_shopping_item(
    shopping_item_id: int,
    request: Request,
    quantity: int = Form(...),
    completed: int = Form(0),
    db: Session = Depends(get_db)
):
    user = require_user(request, db)
    crud.update_shopping_item(db, user.id, shopping_item_id, quantity, completed)

    return RedirectResponse("/shopping-list", status_code=HTTP_303_SEE_OTHER)


@app.post("/shopping-list/{shopping_item_id}/delete")
def delete_shopping_item(
    shopping_item_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    user = require_user(request, db)
    crud.delete_shopping_item(db, user.id, shopping_item_id)

    return RedirectResponse("/shopping-list", status_code=HTTP_303_SEE_OTHER)


@app.get("/analytics")
def analytics_page(request: Request, db: Session = Depends(get_db)):
    user = require_user(request, db)
    items = crud.get_user_inventory(db, user.id)
    scan_logs = crud.get_user_scan_logs(db, user.id, limit=200)
    analytics = build_analytics(items, scan_logs)

    return templates.TemplateResponse(
        request,
        "analytics.html",
        {
            "user": user,
            "analytics": analytics,
            "scan_logs": scan_logs[:8]
        }
    )


@app.get("/recipes")
def recipes_page(request: Request, db: Session = Depends(get_db)):
    user = require_user(request, db)
    items = crud.get_user_inventory(db, user.id)
    suggestions = build_recipe_suggestions(items)

    return templates.TemplateResponse(
        request,
        "recipes.html",
        {
            "user": user,
            "items": items,
            "suggestions": suggestions
        }
    )


@app.get("/scan")
def scan_page(request: Request, db: Session = Depends(get_db)):
    user = require_user(request, db)

    return templates.TemplateResponse(
        request,
        "scan.html",
        {
            "user": user
        }
    )


@app.get("/lookup-product/{barcode}")
def lookup_product(
    barcode: str,
    db: Session = Depends(get_db)
):
    cached_product = crud.get_product_by_barcode(db, barcode)

    if cached_product:
        return {
            "success": True,
            "source": "cache",
            "product": product_to_dict(cached_product)
        }

    product = lookup_product_by_barcode(barcode)

    if product is None:
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "message": "Product not found"
            }
        )

    return {
        "success": True,
        "source": "openfoodfacts",
        "product": product
    }


@app.get("/video-feed")
def video_feed():
    def generate_frames():
        while True:
            frame = camera_service.get_jpeg_frame()

            if frame is None:
                continue

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
            )

    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


# Scanner routes: capture barcode/expiry images and log scan results for analytics.
@app.post("/capture-barcode")
def capture_barcode(request: Request, db: Session = Depends(get_db)):
    user = require_user(request, db)

    try:
        led_service.on()
        barcode = detect_barcode_with_retries()
    finally:
        led_service.off()

    if barcode is None:
        crud.log_scan(db, user.id, "barcode", "No barcode detected", False)

        return JSONResponse({
            "success": False,
            "message": "No barcode detected"
        })

    cached_product = crud.get_product_by_barcode(db, barcode)

    if cached_product:
        product = product_to_dict(cached_product)
    else:
        product = lookup_product_by_barcode(barcode)

    crud.log_scan(db, user.id, "barcode", barcode, True)

    if product is None:
        product = {
            "barcode": barcode,
            "name": "",
            "brand": "",
            "size": "",
            "category": "",
            "full_category": ""
        }

    return JSONResponse({
        "success": True,
        "barcode": barcode,
        "product": product
    })


@app.post("/capture-expiry")
def capture_expiry(request: Request, db: Session = Depends(get_db)):
    user = require_user(request, db)

    try:
        led_service.on()
        frame = camera_service.capture_image()
    finally:
        led_service.off()

    result = extract_expiry_date(frame)

    crud.log_scan(
        db,
        user.id,
        "expiry_ocr",
        result.get("raw_text") or "",
        result.get("date") is not None
    )

    return JSONResponse({
        "success": result.get("date") is not None,
        "date": result.get("date"),
        "raw_text": result.get("raw_text")
    })


@app.post("/save-item")
async def save_item(
    request: Request,
    db: Session = Depends(get_db)
):
    user = require_user(request, db)
    data = await request.json()

    item = schemas.SaveItemRequest(**data)
    saved_item = crud.save_inventory_item(db, user.id, item)

    return {
        "success": True,
        "item_id": saved_item.id
    }


@app.post("/delete-item/{item_id}")
def delete_item(
    item_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    user = require_user(request, db)
    crud.delete_inventory_item(db, user.id, item_id)

    return RedirectResponse("/items", status_code=HTTP_303_SEE_OTHER)


# API route used for returning inventory data as JSON.
@app.get("/api/items", response_model=list[schemas.InventoryResponse])
def api_items(request: Request, db: Session = Depends(get_db)):
    user = require_user(request, db)

    return crud.get_user_inventory(db, user.id)