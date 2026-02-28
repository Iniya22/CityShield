"""
CityShield – JWT Handler
Token creation and validation using python-jose
"""

from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, status

SECRET_KEY = "cityshield-super-secret-key-change-in-production-2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480   # 8 hours


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create a signed JWT with the given claims."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict:
    """Decode and verify a JWT. Raises HTTPException on failure."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject"
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
