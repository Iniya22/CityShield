# ───────────────────────────────────────────────────────────
# app/models.py  –  Pydantic data models (request/response shapes)
# ───────────────────────────────────────────────────────────
from pydantic import BaseModel, EmailStr
from typing import Optional


# ---------- Request models (CLIENT → API) ----------

class UserRegister(BaseModel):
    """Data required to register a new user."""
    username: str
    email:    EmailStr          # validated e-mail address
    password: str               # plain-text password (we will hash it)
    role:     str = "viewer"    # optional role; defaults to "viewer"


class UserLogin(BaseModel):
    """Data required to log in."""
    username: str
    password: str


# ---------- Response models (API → CLIENT) ----------

class Token(BaseModel):
    """Returned after a successful login."""
    access_token: str   # JWT string
    token_type:   str   # always "bearer"


class TokenData(BaseModel):
    """Decoded JWT payload."""
    username: Optional[str] = None


class UserOut(BaseModel):
    """Safe user representation – password is never included."""
    username: str
    email:    str
    role:     str = "viewer"    # ← role is now included in API responses
