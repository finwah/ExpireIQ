from datetime import date
from typing import Optional

from pydantic import BaseModel


class ProductData(BaseModel):
    barcode: str
    name: str
    brand: Optional[str] = None
    size: Optional[str] = None
    category: Optional[str] = None
    full_category: Optional[str] = None


class SaveItemRequest(BaseModel):
    barcode: str
    name: str
    brand: Optional[str] = None
    size: Optional[str] = None
    category: Optional[str] = None
    full_category: Optional[str] = None
    expiration_date: Optional[date] = None
    quantity: int = 1


class ProductResponse(BaseModel):
    id: int
    barcode: str
    name: str
    brand: Optional[str]
    size: Optional[str] = None
    category: Optional[str]
    full_category: Optional[str] = None

    model_config = {"from_attributes": True}


class InventoryResponse(BaseModel):
    id: int
    expiration_date: Optional[date]
    quantity: int
    status: str
    product: ProductResponse

    model_config = {"from_attributes": True}