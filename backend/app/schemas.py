"""
CityShield – Pydantic Schemas
Request/response models for validation and serialization
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ── Auth ─────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None
    role: str = "viewer"


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: str
    is_active: int
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str


# ── Pipelines ────────────────────────────────────────────────────────────────

class PipelineCreate(BaseModel):
    name: str
    zone: str
    material: str
    diameter_mm: float
    length_km: float
    status: str = "active"
    installed_date: Optional[str] = None
    last_inspection: Optional[str] = None


class PipelineUpdate(BaseModel):
    name: Optional[str] = None
    zone: Optional[str] = None
    material: Optional[str] = None
    diameter_mm: Optional[float] = None
    length_km: Optional[float] = None
    status: Optional[str] = None
    installed_date: Optional[str] = None
    last_inspection: Optional[str] = None


class PipelineOut(BaseModel):
    id: int
    name: str
    zone: str
    material: str
    diameter_mm: float
    length_km: float
    status: str
    installed_date: Optional[str]
    last_inspection: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ── Water Tanks ──────────────────────────────────────────────────────────────

class WaterTankCreate(BaseModel):
    name: str
    zone: str
    capacity_liters: float
    current_level_pct: float = 0.0
    status: str = "active"
    tank_type: str = "overhead"
    last_cleaned: Optional[str] = None
    last_inspection: Optional[str] = None


class WaterTankUpdate(BaseModel):
    name: Optional[str] = None
    zone: Optional[str] = None
    capacity_liters: Optional[float] = None
    current_level_pct: Optional[float] = None
    status: Optional[str] = None
    tank_type: Optional[str] = None
    last_cleaned: Optional[str] = None
    last_inspection: Optional[str] = None


class WaterTankOut(BaseModel):
    id: int
    name: str
    zone: str
    capacity_liters: float
    current_level_pct: float
    status: str
    tank_type: str
    last_cleaned: Optional[str]
    last_inspection: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ── Maintenance Logs ─────────────────────────────────────────────────────────

class MaintenanceCreate(BaseModel):
    asset_type: str
    asset_id: int
    asset_name: Optional[str] = None
    description: str
    priority: str = "medium"
    status: str = "open"
    assigned_to: Optional[str] = None


class MaintenanceUpdate(BaseModel):
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    assigned_to: Optional[str] = None


class MaintenanceOut(BaseModel):
    id: int
    asset_type: str
    asset_id: int
    asset_name: Optional[str]
    description: str
    priority: str
    status: str
    assigned_to: Optional[str]
    created_at: Optional[datetime]
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True


# ── Audit Logs ───────────────────────────────────────────────────────────────

class AuditLogOut(BaseModel):
    id: int
    user: str
    action: str
    resource: str
    detail: Optional[str]
    ip_address: Optional[str]
    risk_score: float
    timestamp: Optional[datetime]

    class Config:
        from_attributes = True


# ── Dashboard ────────────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_pipelines: int
    total_tanks: int
    active_pipelines: int
    active_tanks: int
    critical_assets: int
    open_maintenance: int
    recent_audit_events: int
    avg_tank_level: float
