# ───────────────────────────────────────────────────────────
# app/routes.py  –  API endpoints (register, login, protected)
# ───────────────────────────────────────────────────────────
#
# An "endpoint" (or "route") is a URL that clients can call.
# We group related endpoints into an APIRouter and then include
# that router in main.py.
from fastapi import Depends
from app.auth import require_role
from app.database import fake_users_db

from datetime import timedelta

from fastapi import APIRouter, HTTPException, status, Depends

# Import our helper functions and models
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.database import fake_users_db
from app.models import UserRegister, UserLogin, Token, UserOut

# Create a router with a URL prefix.
# Every route in this file will start with /auth
# e.g.  /auth/register,  /auth/login,  /auth/me
router = APIRouter(prefix="/auth", tags=["Authentication"])


# ── 1. REGISTER ─────────────────────────────────────────────
@router.post(
    "/register",
    response_model=UserOut,         # FastAPI will only return fields in UserOut
    status_code=status.HTTP_201_CREATED,  # 201 = "resource created"
    summary="Register a new user",
)
def register(user: UserRegister):
    """
    Create a new account.

    Steps:
      1. Check the username is not already taken.
      2. Hash the password (NEVER store plain-text passwords!).
      3. Save the user in our in-memory database.
      4. Return the new user's public info (no password).
    """
    # Step 1: Reject duplicate usernames
    if user.username in fake_users_db:
        # HTTP 400 Bad Request – the client sent invalid data
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{user.username}' is already taken.",
        )

    # Step 2: Hash the password before storing it
    hashed_pw = hash_password(user.password)

    # Step 3: Store the user record
    fake_users_db[user.username] = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_pw,   # ← hashed, never plain-text
    }

    # Step 4: Return public user data (password is excluded by UserOut)
    return UserOut(username=user.username, email=user.email)


# ── 2. LOGIN ────────────────────────────────────────────────
@router.post(
    "/login",
    response_model=Token,           # respond with {"access_token": "...", "token_type": "bearer"}
    summary="Log in and receive a JWT",
)
def login(credentials: UserLogin):
    """
    Authenticate a user and hand back a JWT access token.

    Steps:
      1. Look the user up by username.
      2. Verify the supplied password against the stored hash.
      3. Create a signed JWT token that expires in N minutes.
      4. Return the token to the client.

    The client stores the token (e.g. in localStorage) and sends it
    in every future request as:
        Authorization: Bearer <token>
    """
    # Step 1: Find the user
    user = fake_users_db.get(credentials.username)
    if not user:
        # Use the same error message for "user not found" and "wrong password"
        # so attackers cannot tell which one is wrong (username enumeration attack)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Step 2: Verify password
    if not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Step 3: Build the token
    # "sub" (subject) is the standard JWT claim for the user identifier.
    token_expiry = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
    data={
    "sub": user["username"],
    "role": user.get("role", "admin")
    },
     expires_delta=token_expiry,
)

    # Step 4: Return the token
    return Token(access_token=access_token, token_type="bearer")


# ── 3. PROTECTED ROUTE (example of a "logged-in only" endpoint) ──
@router.get(
    "/me",
    response_model=UserOut,
    summary="Get the current logged-in user's profile",
)
def read_current_user(
    # Depends(get_current_user) is FastAPI's way of running middleware.
    # FastAPI will:
    #   a) read the Authorization: Bearer <token> header
    #   b) call get_current_user() to validate it
    #   c) inject the returned user dict into this function
    # If the token is missing or invalid, FastAPI returns 401 automatically
    # before this function even runs.
    current_user: dict = Depends(get_current_user),
):
    """
    Return the profile of the currently authenticated user.

    This endpoint requires a valid JWT in the Authorization header.
    If you call it without a token (or with an expired/fake token),
    you will receive HTTP 401 Unauthorized.
    """
    # current_user is the dict we stored in fake_users_db
    return UserOut(
        username=current_user["username"],
        email=current_user["email"],
    )

@router.post("/admin/change-role")
def change_user_role(
    username: str,
    new_role: str,
    admin = Depends(require_role("admin"))
):
    if username not in fake_users_db:
        return {"error": "User not found"}

    fake_users_db[username]["role"] = new_role
    return {
        "message": f"Role updated successfully",
        "username": username,
        "new_role": new_role
    }
