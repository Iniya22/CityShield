"""
CityShield – Role-Based Access Control (RBAC)
FastAPI dependencies for extracting the current user and enforcing roles
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from security.jwt_handler import verify_token

security_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Extract and return the authenticated User from the Bearer token."""
    payload = verify_token(credentials.credentials)
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    return user


def require_role(allowed_roles: list[str]):
    """
    Return a dependency that checks if the current user has one of the
    specified roles.

    Usage:
        @router.get("/", dependencies=[Depends(require_role(["admin", "operator"]))])
    """
    def role_checker(user: User = Depends(get_current_user)):
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
            )
        return user
    return role_checker
