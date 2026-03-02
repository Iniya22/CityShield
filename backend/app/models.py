# ───────────────────────────────────────────────────────────
# app/models.py  –  Pydantic data models (request/response shapes)
# ───────────────────────────────────────────────────────────
#
# Pydantic models describe the shape of data flowing in and out
# of our API.  FastAPI automatically validates requests against
# these models and returns clear error messages when data is wrong.

from pydantic import BaseModel, EmailStr
from typing import Optional


# ---------- Request models (data that the CLIENT sends to us) ----------

class UserRegister(BaseModel):
    """Data required to register a new user."""
    username: str           # e.g. "alice"
    email: EmailStr         # validated e-mail address
    password: str           # plain-text password (we will hash it)


class UserLogin(BaseModel):
    """Data required to log in."""
    username: str
    password: str           # plain-text password; we compare against the stored hash


# ---------- Response models (data that WE send back to the client) ----------

class Token(BaseModel):
    """Returned to the client after a successful login."""
    access_token: str       # the JWT string the client must store
    token_type: str         # always "bearer" — the standard HTTP auth scheme


class TokenData(BaseModel):
    """The decoded payload stored inside the JWT."""
    username: Optional[str] = None   # the 'sub' (subject) claim


class UserOut(BaseModel):
    """Safe user representation — never includes the password."""
    username: str
    email: str
