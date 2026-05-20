from sqlalchemy.orm import Session
from sqlalchemy import func

from . import models, schemas


def create_user(db: Session, username: str, password_hash: str):
    user = models.User(username=username, password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_product_by_barcode(db: Session, barcode: str):
    return db.query(models.Product).filter(models.Product.barcode == barcode).first()


def create_or_update_product(db: Session, item: schemas.SaveItemRequest):
    product = get_product_by_barcode(db, item.barcode)

    if product is None:
        product = models.Product(
            barcode=item.barcode,
            name=item.name,
            brand=item.brand,
            size=item.size,
            category=item.category,
            full_category=item.full_category
        )
        db.add(product)
    else:
        product.name = item.name
        product.brand = item.brand
        product.size = item.size
        product.category = item.category
        product.full_category = item.full_category

    db.commit()
    db.refresh(product)
    return product


def save_inventory_item(db: Session, user_id: int, item: schemas.SaveItemRequest):
    product = create_or_update_product(db, item)

    inventory_item = models.InventoryItem(
        user_id=user_id,
        product_id=product.id,
        expiration_date=item.expiration_date,
        quantity=item.quantity
    )

    db.add(inventory_item)
    db.commit()
    db.refresh(inventory_item)
    return inventory_item


def get_user_inventory(db: Session, user_id: int):
    return db.query(models.InventoryItem).filter(
        models.InventoryItem.user_id == user_id,
        models.InventoryItem.status == "in_fridge"
    ).order_by(models.InventoryItem.expiration_date).all()


def get_inventory_item(db: Session, user_id: int, item_id: int):
    return db.query(models.InventoryItem).filter(
        models.InventoryItem.id == item_id,
        models.InventoryItem.user_id == user_id
    ).first()


def update_inventory_item(db: Session, user_id: int, item_id: int, quantity: int, expiration_date, status: str = "in_fridge"):
    item = get_inventory_item(db, user_id, item_id)

    if item is None:
        return None

    item.quantity = quantity
    item.expiration_date = expiration_date
    item.status = status

    db.commit()
    db.refresh(item)
    return item


def delete_inventory_item(db: Session, user_id: int, item_id: int):
    item = get_inventory_item(db, user_id, item_id)

    if item is None:
        return None

    db.delete(item)
    db.commit()
    return item


def get_inventory_categories(db: Session, user_id: int):
    rows = db.query(models.Product.category).join(models.InventoryItem).filter(
        models.InventoryItem.user_id == user_id,
        models.InventoryItem.status == "in_fridge",
        models.Product.category.isnot(None),
        models.Product.category != ""
    ).distinct().all()

    categories = []

    for row in rows:
        if row[0]:
            for part in row[0].split(","):
                category = part.strip()
                if category and category not in categories:
                    categories.append(category)

    return sorted(categories)


def create_shopping_item(db: Session, user_id: int, name: str, quantity: int = 1, category: str = None):
    existing_item = db.query(models.ShoppingListItem).filter(
        models.ShoppingListItem.user_id == user_id,
        func.lower(models.ShoppingListItem.name) == name.lower(),
        models.ShoppingListItem.completed == 0
    ).first()

    if existing_item:
        existing_item.quantity += quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item

    item = models.ShoppingListItem(
        user_id=user_id,
        name=name,
        quantity=quantity,
        category=category
    )

    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def add_inventory_item_to_shopping_list(db: Session, user_id: int, item_id: int):
    inventory_item = get_inventory_item(db, user_id, item_id)

    if inventory_item is None:
        return None

    return create_shopping_item(
        db=db,
        user_id=user_id,
        name=inventory_item.product.name,
        quantity=1,
        category=inventory_item.product.category
    )


def get_shopping_list(db: Session, user_id: int):
    return db.query(models.ShoppingListItem).filter(
        models.ShoppingListItem.user_id == user_id
    ).order_by(
        models.ShoppingListItem.completed,
        models.ShoppingListItem.created_at.desc()
    ).all()


def update_shopping_item(db: Session, user_id: int, shopping_item_id: int, quantity: int, completed: int):
    item = db.query(models.ShoppingListItem).filter(
        models.ShoppingListItem.id == shopping_item_id,
        models.ShoppingListItem.user_id == user_id
    ).first()

    if item is None:
        return None

    item.quantity = quantity
    item.completed = completed
    db.commit()
    db.refresh(item)
    return item


def delete_shopping_item(db: Session, user_id: int, shopping_item_id: int):
    item = db.query(models.ShoppingListItem).filter(
        models.ShoppingListItem.id == shopping_item_id,
        models.ShoppingListItem.user_id == user_id
    ).first()

    if item is None:
        return None

    db.delete(item)
    db.commit()
    return item


def log_scan(db: Session, user_id: int, scan_type: str, raw_result: str, success: bool):
    log = models.ScanLog(
        user_id=user_id,
        scan_type=scan_type,
        raw_result=raw_result,
        success=1 if success else 0
    )

    db.add(log)
    db.commit()
    db.refresh(log)
    return log

def get_user_scan_logs(db: Session, user_id: int, limit: int = 100):
    return db.query(models.ScanLog).filter(
        models.ScanLog.user_id == user_id
    ).order_by(
        models.ScanLog.scanned_at.desc()
    ).limit(limit).all()


def get_recent_scan_logs(db: Session, user_id: int, limit: int = 8):
    return db.query(models.ScanLog).filter(
        models.ScanLog.user_id == user_id
    ).order_by(
        models.ScanLog.scanned_at.desc()
    ).limit(limit).all()