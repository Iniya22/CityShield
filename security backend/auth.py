# ============================================================
# auth.py — JWT Token Logic & Password Hashing
# ============================================================
# This file handles everything related to security:
#   1. Hashing passwords (so we never store raw passwords)
#   2. Creating JWT tokens (given to users after login)
#   3. Verifying JWT tokens (to protect private routes)
# ============================================================

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

import models
from database import get_db
from schemas import TokenData


# ---------------------------------------------------------------------------
# SECRET KEY & ALGORITHM
# ---------------------------------------------------------------------------
# The SECRET_KEY is used to digitally "sign" the JWT token.
# Only the server knows this key, so only the server can create valid tokens.
# The ALGORITHM tells JWT which math to use when signing.
#   HS256 = HMAC + SHA-256, the most common choice.
#
# ⚠️  IMPORTANT: In a real app, store the SECRET_KEY in a .env file —
#     NEVER hardcode it in your code or push it to GitHub!
# ---------------------------------------------------------------------------
SECRET_KEY = "your-super-secret-key-change-this-in-production"
ALGORITHM = "HS256"

# How long the token stays valid (in minutes)
# After this time, the token expires and the user must log in again
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# ---------------------------------------------------------------------------
# PASSWORD HASHING
# ---------------------------------------------------------------------------
# CryptContext sets up bcrypt, a slow and secure hashing algorithm.
# "deprecated=auto" means old hashes are automatically upgraded.
# ---------------------------------------------------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------------------------------------------------------------------
# OAUTH2 SCHEME
# ---------------------------------------------------------------------------
# This tells FastAPI where to find the token in incoming requests.
# Clients must send the token in the HTTP header like this:
#     Authorization: Bearer <token>
# "tokenUrl" points to the login endpoint (used in /docs UI)
# ---------------------------------------------------------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


# ===========================================================================
# HELPER FUNCTIONS
# ===========================================================================

def hash_password(plain_password: str) -> str:
    """
    Takes a plain text password and returns a secure bcrypt hash.
    
    Example:
        hash_password("mypassword123") → "$2b$12$eImiTXuWVxfM37uY4Jahl..."
    
    The hash looks random but is reproducible — bcrypt verifies it later.
    """
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Checks if a plain password matches a stored hash.
    
    Returns True if they match, False otherwise.
    This is called during login to confirm the password is correct.
    
    We NEVER reverse the hash — bcrypt re-hashes and compares.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates and returns a signed JWT token.
    
    Parameters:
        data         — a dict with the payload to encode (e.g. {"sub": "alice"})
        expires_delta — how long until the token expires (default: 30 minutes)
    
    A JWT has 3 parts separated by dots: header.payload.signature
    The payload contains {"sub": "alice", "exp": <timestamp>}
    """
    to_encode = data.copy()  # Don't mutate the original dict

    # Calculate the exact expiry time
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # "exp" (expiry) is a standard JWT claim — jose uses it automatically
    to_encode.update({"exp": expire})

    # Sign and encode the token using our secret key and algorithm
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> TokenData:
    """
    Decodes and validates a JWT token.
    
    Returns TokenData (contains username) if valid.
    Raises HTTP 401 if the token is invalid, expired, or tampered with.
    """
    # This is the error we raise if anything goes wrong with the token
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},  # Standard header for 401 errors
    )

    try:
        # Decode the JWT — this also checks the signature and expiry automatically
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # "sub" (subject) is a standard JWT claim — we store the username here
        username: str = payload.get("sub")

        if username is None:
            raise credentials_exception  # Token has no username — invalid

        return TokenData(username=username)  # Return the username from the token

    except JWTError:
        # Token was tampered with, has wrong format, or has expired
        raise credentials_exception


def get_current_user(
    token: str = Depends(oauth2_scheme),  # FastAPI auto-extracts token from header
    db: Session = Depends(get_db)         # FastAPI auto-provides a DB session
):
    """
    FastAPI Dependency — Protects routes by verifying the JWT token.
    
    Usage in routes:
        @app.get("/me")
        def me(current_user = Depends(get_current_user)):
            ...
    
    FastAPI will:
        1. Read the "Authorization: Bearer <token>" header
        2. Pass the token to verify_token()
        3. Look up the user in the database
        4. Provide the User object to the route handler
        5. OR raise HTTP 401 if the token is missing/invalid
    """
    # Step 1: Verify the token and extract the username
    token_data = verify_token(token)

    # Step 2: Fetch the actual user from the database
    user = db.query(models.User).filter(
        models.User.username == token_data.username
    ).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User belonging to this token no longer exists"
        )

    return user  # The route handler receives this User object
