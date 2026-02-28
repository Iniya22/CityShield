"""
CityShield – Auth Router
Login, register, and user info endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserLogin, UserOut, Token
from security.jwt_handler import create_access_token
from security.rbac import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/register", response_model=UserOut, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    existing = db.query(User).filter(
        (User.username == data.username) | (User.email == data.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    user = User(
        username=data.username,
        email=data.email,
        hashed_password=pwd_context.hash(data.password),
        full_name=data.full_name,
        role=data.role if data.role in ("admin", "operator", "viewer") else "viewer"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate and return a JWT."""
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not pwd_context.verify(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    token = create_access_token(data={"sub": user.username, "role": user.role})
    return Token(access_token=token, role=user.role, username=user.username)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    return user
