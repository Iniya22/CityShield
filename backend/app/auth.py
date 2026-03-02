# ───────────────────────────────────────────────────────────
# app/auth.py  –  All authentication / JWT helper functions
# ───────────────────────────────────────────────────────────

from datetime import datetime, timedelta, timezone
from typing import Optional

# jose = JavaScript Object Signing and Encryption library for Python.
# It handles creating (encoding) and reading (decoding) JWT tokens.
from jose import JWTError, jwt

# passlib is a password hashing library.
# CryptContext lets us choose a hashing algorithm (bcrypt is the gold standard).
from passlib.context import CryptContext

# FastAPI security utilities
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Our own files
from app.config import SECRET_KEY, ALGORITHM
from app.models import TokenData
from app.database import fake_users_db


# ── Password hashing ────────────────────────────────────────
# We create a CryptContext that uses bcrypt.
# bcrypt applies a one-way hash to the password, so we never store
# the raw password — only the hash.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """
    Turn a plain-text password into a bcrypt hash.
    
    Example:
        hash_password("secret123")
        → "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
    
    This string looks random, so even if someone steals the database
    they cannot easily discover the original password.
    """
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Check whether a plain-text password matches a stored hash.
    
    passlib re-hashes the plain password with the same salt that was
    embedded in the stored hash, then compares the results.
    Returns True if they match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


# ── JWT token creation ───────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a signed JWT access token.

    Parameters
    ----------
    data : dict
        The payload to encode.  Typically {"sub": username}.
        "sub" (subject) is the standard JWT claim for the user identifier.
    expires_delta : timedelta, optional
        How long until the token expires.  Defaults to 15 minutes.

    Returns
    -------
    str
        The encoded JWT string, e.g.
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJh..."
    
    How a JWT is built
    ------------------
    A JWT has three parts separated by dots:
        HEADER.PAYLOAD.SIGNATURE

        • Header  – algorithm name (HS256)
        • Payload – your data + expiry time
        • Signature – HMAC of (header + payload) using SECRET_KEY
                      → proves the token was created by our server
    """
    # Copy the data so we don't mutate the caller's dict
    to_encode = data.copy()

    # Calculate the expiry timestamp
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    # "exp" is a standard JWT claim; the library uses it automatically
    to_encode.update({"exp": expire})

    # jwt.encode() signs the payload and returns the compact token string
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ── Token extraction from requests ──────────────────────────
#
# OAuth2PasswordBearer tells FastAPI:
#   "Expect an Authorization: Bearer <token> header on protected routes."
#   "If it's missing, return HTTP 401 automatically."
#
# tokenUrl="/auth/login" is just documentation — it tells the
# Swagger UI which endpoint issues tokens so it can show a login form.
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    token = credentials.credentials
    """
    Dependency function: validates the JWT and returns the current user.
    
    
    FastAPI calls this automatically when a route declares
        current_user = Depends(get_current_user)

    Flow
    ----
    1. FastAPI reads the Bearer token from the Authorization header.
    2. We decode & verify the token using our SECRET_KEY.
    3. We extract the username from the "sub" claim.
    4. We look that user up in the database.
    5. We return the user dict so the route can use it.

    If anything is wrong (expired, tampered, user deleted) we raise
    HTTP 401 Unauthorized.
    """
    # Define the error we'll raise for any authentication failure
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        # WWW-Authenticate header is required by the OAuth2 spec
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode and verify the token.
        # jose raises JWTError if the signature is wrong or token is expired.
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Extract the "sub" claim (username) from the payload
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception

        # Wrap in our TokenData model for type safety
        token_data = TokenData(username=username)

    except JWTError:
        # Token is invalid for any reason (expired, tampered, wrong key…)
        raise credentials_exception

    # Look the user up in our fake database
    user = fake_users_db.get(token_data.username)
    if user is None:
        raise credentials_exception   # user was deleted after token was issued

    return {
    "username": user["username"],
    "email": user["email"],
    "role": payload.get("role", "viewer")
}
# ── Role-based access control (RBAC) ─────────────────────────

def require_role(required_role: str):
    def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role", "viewer")

        if user_role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: insufficient permissions"
            )

        return current_user

    return role_checker