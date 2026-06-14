"""
seed.py
-------
Optional helper that fills the database with sample data so the site
looks alive during your demo / viva.

Run it once AFTER the tables are created:
    python seed.py

It creates:
  - an admin account   ->  admin@shop.com   / admin123
  - a customer account ->  user@shop.com    / user123
  - a few categories and products
"""

from database import SessionLocal, engine, Base
import models
import auth

# Make sure tables exist.
Base.metadata.create_all(bind=engine)

db = SessionLocal()


def get_or_create_user(name, email, password, role):
    user = db.query(models.User).filter(models.User.email == email).first()
    if user:
        return user
    user = models.User(
        name=name, email=email, password=auth.hash_password(password), role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_or_create_category(name):
    cat = db.query(models.Category).filter(
        models.Category.category_name == name
    ).first()
    if cat:
        return cat
    cat = models.Category(category_name=name)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


def main():
    # Users
    get_or_create_user("Admin User", "admin@shop.com", "admin123", "admin")
    get_or_create_user("Demo Customer", "user@shop.com", "user123", "customer")

    # Categories
    electronics = get_or_create_category("Electronics")
    clothing = get_or_create_category("Clothing")
    books = get_or_create_category("Books")

    # Products (only add if the products table is empty, to avoid duplicates)
    if db.query(models.Product).count() == 0:
        sample_products = [
            models.Product(name="Wireless Headphones", description="Bluetooth over-ear headphones with noise cancellation.", price=59.99, stock=25, category_id=electronics.id),
            models.Product(name="Smart Watch", description="Fitness tracking smart watch with heart-rate monitor.", price=89.99, stock=15, category_id=electronics.id),
            models.Product(name="USB-C Charger", description="65W fast charging adapter.", price=19.99, stock=40, category_id=electronics.id),
            models.Product(name="Cotton T-Shirt", description="Comfortable 100% cotton t-shirt.", price=12.99, stock=60, category_id=clothing.id),
            models.Product(name="Denim Jacket", description="Classic blue denim jacket.", price=45.00, stock=20, category_id=clothing.id),
            models.Product(name="Python Crash Course", description="Beginner-friendly programming book.", price=29.99, stock=30, category_id=books.id),
            models.Product(name="Clean Code", description="A handbook of agile software craftsmanship.", price=34.99, stock=18, category_id=books.id),
        ]
        db.add_all(sample_products)
        db.commit()

    print("Seed data inserted successfully.")
    print("Admin login    -> admin@shop.com / admin123")
    print("Customer login -> user@shop.com  / user123")


if __name__ == "__main__":
    main()
    db.close()
