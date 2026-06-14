"""
main.py
-------
The heart of the backend. This file creates the FastAPI application and
defines all 18 REST API endpoints described in the Phase 1 documentation:

  AUTH        POST /register, POST /login
  PRODUCTS    POST /products, GET /products, GET /products/{id},
              PUT /products/{id}, DELETE /products/{id}
  CATEGORIES  POST /categories, GET /categories
  CART        POST /cart, GET /cart/{user_id}, PUT /cart/{id}, DELETE /cart/{id}
  ORDERS      POST /orders, GET /orders, GET /orders/{id},
              PUT /orders/{id}, DELETE /orders/{id}
  DASHBOARD   GET /dashboard

Run locally with:   uvicorn main:app --reload
Interactive docs:   http://127.0.0.1:8000/docs
"""

from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func

import models
import schemas
import auth
from database import engine, get_db, Base

# Create all tables in the database the first time the app starts.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="E-Commerce Management System API",
    description="FastAPI backend for the OSSD final semester project.",
    version="1.0.0",
)

# CORS lets the frontend (served from a different origin) call this API.
# For a class project we allow all origins; tighten this in real production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """Simple health-check so you can confirm the API is alive."""
    return {"message": "E-Commerce API is running", "docs": "/docs"}


# =========================================================
# 1 & 2.  AUTHENTICATION
# =========================================================
@app.post("/register", response_model=schemas.Token, tags=["Auth"])
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Create a new user. Email must be unique. Password is hashed with bcrypt."""
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = models.User(
        name=user.name,
        email=user.email,
        password=auth.hash_password(user.password),
        role=user.role or "customer",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = auth.create_access_token({"user_id": new_user.id, "role": new_user.role})
    return {"access_token": token, "token_type": "bearer", "user": new_user}


@app.post("/login", response_model=schemas.Token, tags=["Auth"])
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """Authenticate a user and return a JWT token plus basic user info."""
    user = db.query(models.User).filter(models.User.email == credentials.email).first()
    if not user or not auth.verify_password(credentials.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = auth.create_access_token({"user_id": user.id, "role": user.role})
    return {"access_token": token, "token_type": "bearer", "user": user}


# =========================================================
# CATEGORIES
# =========================================================
@app.post("/categories", response_model=schemas.CategoryOut, tags=["Categories"])
def create_category(
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(auth.require_admin),
):
    """Add a new category (admin only)."""
    if db.query(models.Category).filter(
        models.Category.category_name == category.category_name
    ).first():
        raise HTTPException(status_code=400, detail="Category already exists")
    new_cat = models.Category(category_name=category.category_name)
    db.add(new_cat)
    db.commit()
    db.refresh(new_cat)
    return new_cat


@app.get("/categories", response_model=List[schemas.CategoryOut], tags=["Categories"])
def get_categories(db: Session = Depends(get_db)):
    """Return all categories (public)."""
    return db.query(models.Category).all()


# =========================================================
# PRODUCTS
# =========================================================
@app.post("/products", response_model=schemas.ProductOut, tags=["Products"])
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(auth.require_admin),
):
    """Add a new product (admin only)."""
    new_product = models.Product(**product.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@app.get("/products", response_model=List[schemas.ProductOut], tags=["Products"])
def get_products(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search by product name"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
):
    """
    Return all products (public).
    Supports SEARCH (?search=phone) and FILTER (?category_id=2) via query params,
    which powers the search bar and category filter on the products page.
    """
    query = db.query(models.Product)
    if search:
        query = query.filter(models.Product.name.ilike(f"%{search}%"))
    if category_id is not None:
        query = query.filter(models.Product.category_id == category_id)
    return query.all()


@app.get("/products/{product_id}", response_model=schemas.ProductOut, tags=["Products"])
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Return a single product by its id (public)."""
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.put("/products/{product_id}", response_model=schemas.ProductOut, tags=["Products"])
def update_product(
    product_id: int,
    updates: schemas.ProductUpdate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(auth.require_admin),
):
    """Update an existing product (admin only). Only sent fields are changed."""
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # exclude_unset=True => only update the fields the client actually sent.
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


@app.delete("/products/{product_id}", tags=["Products"])
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(auth.require_admin),
):
    """Delete a product (admin only)."""
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}


# =========================================================
# CART
# =========================================================
@app.post("/cart", response_model=schemas.CartOut, tags=["Cart"])
def add_to_cart(
    item: schemas.CartCreate,
    db: Session = Depends(get_db),
    current: models.User = Depends(auth.get_current_user),
):
    """Add a product to the cart. If it is already there, increase quantity."""
    product = db.query(models.Product).filter(
        models.Product.id == item.product_id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    existing = (
        db.query(models.Cart)
        .filter(
            models.Cart.user_id == item.user_id,
            models.Cart.product_id == item.product_id,
        )
        .first()
    )
    if existing:
        existing.quantity += item.quantity
        db.commit()
        db.refresh(existing)
        return existing

    new_item = models.Cart(
        user_id=item.user_id,
        product_id=item.product_id,
        quantity=item.quantity,
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@app.get("/cart/{user_id}", response_model=List[schemas.CartOut], tags=["Cart"])
def get_cart(
    user_id: int,
    db: Session = Depends(get_db),
    current: models.User = Depends(auth.get_current_user),
):
    """View all cart items for a specific user (with product details attached)."""
    return db.query(models.Cart).filter(models.Cart.user_id == user_id).all()


@app.put("/cart/{cart_id}", response_model=schemas.CartOut, tags=["Cart"])
def update_cart(
    cart_id: int,
    update: schemas.CartUpdate,
    db: Session = Depends(get_db),
    current: models.User = Depends(auth.get_current_user),
):
    """Update the quantity of a cart item."""
    item = db.query(models.Cart).filter(models.Cart.id == cart_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    item.quantity = update.quantity
    db.commit()
    db.refresh(item)
    return item


@app.delete("/cart/{cart_id}", tags=["Cart"])
def delete_cart_item(
    cart_id: int,
    db: Session = Depends(get_db),
    current: models.User = Depends(auth.get_current_user),
):
    """Remove an item from the cart."""
    item = db.query(models.Cart).filter(models.Cart.id == cart_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    db.delete(item)
    db.commit()
    return {"message": "Item removed from cart"}


# =========================================================
# ORDERS
# =========================================================
@app.post("/orders", response_model=schemas.OrderOut, tags=["Orders"])
def place_order(
    order: schemas.OrderCreate,
    db: Session = Depends(get_db),
    current: models.User = Depends(auth.get_current_user),
):
    """
    Place a new order.
    Steps:
      1. For each item, check the product exists and has enough stock.
      2. Compute the total price from CURRENT product prices.
      3. Reduce product stock.
      4. Save the order + its order_items.
      5. Clear that user's cart.
    """
    if not order.items:
        raise HTTPException(status_code=400, detail="Order has no items")

    new_order = models.Order(user_id=order.user_id, total_price=0.0, status="pending")
    db.add(new_order)
    db.flush()  # get new_order.id without committing yet

    total = 0.0
    for line in order.items:
        product = db.query(models.Product).filter(
            models.Product.id == line.product_id
        ).first()
        if not product:
            raise HTTPException(
                status_code=404, detail=f"Product {line.product_id} not found"
            )
        if product.stock < line.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for '{product.name}'",
            )

        product.stock -= line.quantity
        total += product.price * line.quantity

        db.add(models.OrderItem(
            order_id=new_order.id,
            product_id=product.id,
            quantity=line.quantity,
            price=product.price,
        ))

    new_order.total_price = total

    # Empty the user's cart after a successful order.
    db.query(models.Cart).filter(models.Cart.user_id == order.user_id).delete()

    db.commit()
    db.refresh(new_order)
    return new_order


@app.get("/orders", response_model=List[schemas.OrderOut], tags=["Orders"])
def get_orders(
    db: Session = Depends(get_db),
    user_id: Optional[int] = Query(None, description="Filter orders by user"),
    current: models.User = Depends(auth.get_current_user),
):
    """
    View orders.
    - Admins see all orders (and can filter by ?user_id=).
    - Customers only ever see their own orders.
    """
    query = db.query(models.Order)
    if current.role != "admin":
        query = query.filter(models.Order.user_id == current.id)
    elif user_id is not None:
        query = query.filter(models.Order.user_id == user_id)
    return query.order_by(models.Order.id.desc()).all()


@app.get("/orders/{order_id}", response_model=schemas.OrderOut, tags=["Orders"])
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current: models.User = Depends(auth.get_current_user),
):
    """View a single order. Customers can only view their own orders."""
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if current.role != "admin" and order.user_id != current.id:
        raise HTTPException(status_code=403, detail="Not allowed to view this order")
    return order


@app.put("/orders/{order_id}", response_model=schemas.OrderOut, tags=["Orders"])
def update_order_status(
    order_id: int,
    update: schemas.OrderStatusUpdate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(auth.require_admin),
):
    """Update an order's status, e.g. pending -> shipped -> delivered (admin only)."""
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = update.status
    db.commit()
    db.refresh(order)
    return order


@app.delete("/orders/{order_id}", tags=["Orders"])
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(auth.require_admin),
):
    """Delete an order and its items (admin only)."""
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    db.delete(order)
    db.commit()
    return {"message": "Order deleted successfully"}


# =========================================================
# DASHBOARD
# =========================================================
@app.get("/dashboard", response_model=schemas.DashboardOut, tags=["Dashboard"])
def dashboard(
    db: Session = Depends(get_db),
    admin: models.User = Depends(auth.require_admin),
):
    """Return summary analytics for the admin dashboard (admin only)."""
    total_sales = db.query(func.coalesce(func.sum(models.Order.total_price), 0.0)).scalar()
    pending = db.query(models.Order).filter(models.Order.status == "pending").count()
    return {
        "total_users": db.query(models.User).count(),
        "total_products": db.query(models.Product).count(),
        "total_orders": db.query(models.Order).count(),
        "total_categories": db.query(models.Category).count(),
        "total_sales": float(total_sales),
        "pending_orders": pending,
    }
