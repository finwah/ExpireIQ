from fastapi import Request, HTTPException
from itsdangerous import URLSafeSerializer, BadSignature
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from . import models

SECRET_KEY = "change-this-secret-key-before-final-demo"

serializer = URLSafeSerializer(SECRET_KEY)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str):
    return pwd_context.verify(password, password_hash)


def create_session_cookie(user_id: int):
    return serializer.dumps({"user_id": user_id})


def get_user_id_from_cookie(request: Request):
    cookie = request.cookies.get("session")

    if not cookie:
        return None

    try:
        data = serializer.loads(cookie)
        return data.get("user_id")
    except BadSignature:
        return None


def get_current_user(request: Request, db: Session):
    user_id = get_user_id_from_cookie(request)

    if user_id is None:
        raise HTTPException(status_code=401, detail="Not logged in")

    user = db.query(models.User).filter(models.User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid user")

    return user