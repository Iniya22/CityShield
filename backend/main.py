# ───────────────────────────────────────────────────────────
# main.py  –  Application entry point (API + Frontend merged)
# ───────────────────────────────────────────────────────────
#
# Run with:
#     uvicorn main:app --reload
#
# After merging, everything lives on ONE port (8000):
#   • API  →  http://127.0.0.1:8000/auth/...
#   • UI   →  http://127.0.0.1:8000/login.html
#              http://127.0.0.1:8000/register.html
#              http://127.0.0.1:8000/dashboard.html

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles   # ← serves HTML/CSS/JS
from fastapi.responses import RedirectResponse
from app.routes import router   # our authentication router

# ── Path to the frontend folder (one level up from backend/) ──
# __file__ is this file (main.py), so we go up one directory.
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend')

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

# ── CORS Middleware ──────────────────────────────────────────
# Still useful for Swagger UI / external tools calling the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Routes (must be registered BEFORE static file mount) ─
app.include_router(router)

# ── Root redirect → login page ───────────────────────────────
# Typing http://127.0.0.1:8000 in the browser now opens login.
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/login.html")

# ── Serve the frontend as static files ──────────────────────
# Mount LAST so API routes always take priority.
# html=True means a bare directory URL tries to serve index.html.
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

