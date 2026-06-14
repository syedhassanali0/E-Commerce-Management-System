"""
models.py
---------
Defines the 6 database tables as Python classes (SQLAlchemy ORM models).
These match the schema described in your Phase 1 documentation exactly:

  Users, Categories, Products, Cart, Orders, Order_Items

Relationships:
  Categories 1 --- * Products
  Users      1 --- * Orders   1 --- * Order_Items
  Users      1 --- * Cart      * --- 1 Products
"""

from datetime import date
from sqlalchemy import (
    Column, Integer, String, Float, Text, Date, ForeignKey
)
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)          # stores the bcrypt HASH
    role = Column(String, default="customer")          # 'customer' or 'admin'

    # One user can have many orders and many cart items.
    orders = relationship("Order", back_populates="user")
    cart_items = relationship("Cart", back_populates="user")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String, unique=True, nullable=False)

    # One category can contain many products.
    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, default="")
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    category = relationship("Category", back_populates="products")


class Cart(Base):
    __tablename__ = "cart"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1)

    user = relationship("User", back_populates="cart_items")
    product = relationship("Product")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_price = Column(Float, default=0.0)
    order_date = Column(Date, default=date.today)
    status = Column(String, default="pending")   # pending / shipped / delivered

    user = relationship("User", back_populates="orders")
    # One order has many order items. Deleting an order deletes its items.
    items = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1)
    price = Column(Float, default=0.0)           # price at time of purchase

    order = relationship("Order", back_populates="items")
    product = relationship("Product")
