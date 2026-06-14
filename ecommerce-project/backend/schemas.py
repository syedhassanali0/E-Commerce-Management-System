"""
schemas.py
----------
Pydantic models (called "schemas") describe the shape of the JSON that
goes IN to the API and comes OUT of it. FastAPI uses them to:
  - validate incoming request bodies automatically
  - convert database objects into clean JSON responses
  - generate the interactive /docs page

Naming convention used here:
  XCreate  -> data the client SENDS to create something
  XUpdate  -> data the client SENDS to update something
  XOut     -> data the API SENDS BACK to the client
"""

from datetime import date
from typing import Optional, List
from pydantic import BaseModel, EmailStr


# ---------- Auth / Users ----------
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Optional[str] = "customer"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True   # allow building this from an ORM object


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Categories ----------
class CategoryCreate(BaseModel):
    category_name: str


class CategoryOut(BaseModel):
    id: int
    category_name: str

    class Config:
        from_attributes = True


# ---------- Products ----------
class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    price: float
    stock: Optional[int] = 0
    category_id: Optional[int] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    category_id: Optional[int] = None


class ProductOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    stock: int
    category_id: Optional[int]

    class Config:
        from_attributes = True


# ---------- Cart ----------
class CartCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int = 1


class CartUpdate(BaseModel):
    quantity: int


class CartOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    product: Optional[ProductOut] = None   # nested product details

    class Config:
        from_attributes = True


# ---------- Orders ----------
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = 1


class OrderCreate(BaseModel):
    user_id: int
    items: List[OrderItemCreate]


class OrderStatusUpdate(BaseModel):
    status: str


class OrderItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float

    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    id: int
    user_id: int
    total_price: float
    order_date: date
    status: str
    items: List[OrderItemOut] = []

    class Config:
        from_attributes = True


# ---------- Dashboard ----------
class DashboardOut(BaseModel):
    total_users: int
    total_products: int
    total_orders: int
    total_categories: int
    total_sales: float
    pending_orders: int
