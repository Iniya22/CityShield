# ───────────────────────────────────────────────────────────
# main.py  –  Application entry point
# ───────────────────────────────────────────────────────────
#
# This file creates the FastAPI application, registers all routers,
# and starts the HTTP server when you run:
#
#     uvicorn main:app --reload
#                 ^^^
#                 "app" refers to the variable `app` defined below.
# ── reload flag ──────────────────────────────────────────────
# --reload makes uvicorn restart automatically whenever you save a file.
# Great for development; remove it in production.

from fastapi import FastAPI
from app.routes import router   # our authentication router

# ── Create the FastAPI application ──────────────────────────
app = FastAPI(
    title="CityShield Auth API",
    description=(
        "Beginner-friendly FastAPI login system with JWT.\n\n"
        "## How to test\n"
        "1. **POST /auth/register** – create an account\n"
        "2. **POST /auth/login** – get a JWT token\n"
        "3. Click **Authorize 🔒** (top right), paste the token\n"
        "4. **GET /auth/me** – see your profile (protected)\n"
    ),
    version="1.0.0",
)

# ── Register the router ──────────────────────────────────────
# This attaches all routes from routes.py (register, login, me)
# to our application.
app.include_router(router)


# ── Root health-check ────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    """Simple health-check so you know the server is running."""
    return {"message": "CityShield Auth API is running 🚀"}
