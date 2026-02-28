"""
CityShield – Main Application
FastAPI entry point with router registration and middleware
"""

import sys, os

# Ensure the backend directory is on sys.path so both `app` and `security`
# packages can be imported regardless of the working directory.
_backend_dir = os.path.dirname(os.path.abspath(__file__))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import engine, get_db, Base
from app.models import AuditLog
from app.schemas import DashboardStats, AuditLogOut
from app import crud
from app.routers import pipelines, watertanks, maintenance
from security.auth import router as auth_router
from security.middleware import AuditMiddleware
from security.rbac import require_role

from typing import List

# ── Create tables ────────────────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="CityShield",
    description="Zero-trust security architecture for smart urban infrastructure",
    version="1.0.0"
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Audit Middleware ─────────────────────────────────────────────────────────
app.add_middleware(AuditMiddleware)

# ── Routers ──────────────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(pipelines.router)
app.include_router(watertanks.router)
app.include_router(maintenance.router)


# ── Dashboard endpoint ───────────────────────────────────────────────────────
@app.get("/api/dashboard", response_model=DashboardStats, tags=["Dashboard"])
def dashboard(db: Session = Depends(get_db),
              _user=Depends(require_role(["admin", "operator", "viewer"]))):
    return crud.get_dashboard_stats(db)


# ── Audit log endpoint (admin only) ─────────────────────────────────────────
@app.get("/api/audit", response_model=List[AuditLogOut], tags=["Audit"])
def audit_logs(skip: int = 0, limit: int = 200,
               db: Session = Depends(get_db),
               _user=Depends(require_role(["admin"]))):
    return crud.get_audit_logs(db, skip, limit)


# ── Serve React frontend (production build) ─────────────────────────────────
frontend_dir = os.path.join(os.path.dirname(_backend_dir), "frontend", "dist")
if os.path.isdir(frontend_dir):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dir, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = os.path.join(frontend_dir, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dir, "index.html"))


# ── Health check ─────────────────────────────────────────────────────────────
@app.get("/api/health", tags=["Health"])
def health():
    return {"status": "ok", "service": "CityShield"}
