"""
auth.py
-------
Security helpers used by the API:
  - Hash and verify passwords with bcrypt (so plain passwords are never stored)
  - Create and decode JWT tokens (so a logged-in user can prove who they are)
  - get_current_user / require_admin dependencies that protect endpoints

We use the `bcrypt` and `PyJWT` libraries directly (no passlib) to avoid
version-compatibility issues that students often hit.
"""

import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt  # provided by the PyJWT package
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_db
import models

# Secret key used to SIGN tokens. In production, set JWT_SECRET in .env.
SECRET_KEY = os.getenv("JWT_SECRET", "change-this-secret-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # token valid for 24 hours

# Tells FastAPI where the login endpoint is (used by the /docs "Authorize" button).
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# ---------- Password hashing ----------
def hash_password(plain_password: str) -> str:
    """Turn a plain password into a salted bcrypt hash (stored in the DB)."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a plain password against the stored hash. Returns True/False."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )
    except ValueError:
        return False


# ---------- JWT tokens ----------
def create_access_token(data: dict) -> str:
    """Create a signed JWT containing the given data plus an expiry time."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    """
    Dependency that reads the JWT from the Authorization header,
    verifies it, and returns the matching User from the database.
    Protected endpoints add: current = Depends(get_current_user)
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


def require_admin(current: models.User = Depends(get_current_user)) -> models.User:
    """Dependency that only allows admin users through."""
    if current.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current
