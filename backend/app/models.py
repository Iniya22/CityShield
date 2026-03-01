"""
CityShield – ORM Models
Defines all database tables for the Urban Water Supply system
"""

from sqlalchemy import (
    Column, Integer, String, Float, Text, DateTime, Enum, ForeignKey
)
from sqlalchemy.sql import func
from app.database import Base
import enum


# ── Enums ────────────────────────────────────────────────────────────────────

class UserRole(str, enum.Enum):
    admin = "admin"
    operator = "operator"
    viewer = "viewer"


class AssetStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    maintenance = "maintenance"
    critical = "critical"


class Priority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class MaintenanceStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"


# ── Users ────────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(String(20), default=UserRole.viewer, nullable=False)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())


# ── Pipelines ────────────────────────────────────────────────────────────────

class Pipeline(Base):
    __tablename__ = "pipelines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    zone = Column(String(50), nullable=False)
    material = Column(String(50), nullable=False)
    diameter_mm = Column(Float, nullable=False)
    length_km = Column(Float, nullable=False)
    status = Column(String(20), default=AssetStatus.active, nullable=False)
    installed_date = Column(String(20), nullable=True)
    last_inspection = Column(String(20), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


# ── Water Tanks ──────────────────────────────────────────────────────────────

class WaterTank(Base):
    __tablename__ = "water_tanks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    zone = Column(String(50), nullable=False)
    capacity_liters = Column(Float, nullable=False)
    current_level_pct = Column(Float, default=0.0)
    status = Column(String(20), default=AssetStatus.active, nullable=False)
    tank_type = Column(String(50), default="overhead")
    last_cleaned = Column(String(20), nullable=True)
    last_inspection = Column(String(20), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


# ── Maintenance Logs ─────────────────────────────────────────────────────────

class MaintenanceLog(Base):
    __tablename__ = "maintenance_logs"

    id = Column(Integer, primary_key=True, index=True)
    asset_type = Column(String(20), nullable=False)          # "pipeline" or "tank"
    asset_id = Column(Integer, nullable=False)
    asset_name = Column(String(100), nullable=True)
    description = Column(Text, nullable=False)
    priority = Column(String(20), default=Priority.medium, nullable=False)
    status = Column(String(20), default=MaintenanceStatus.open, nullable=False)
    assigned_to = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    resolved_at = Column(DateTime, nullable=True)


# ── Audit Logs ───────────────────────────────────────────────────────────────

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user = Column(String(50), nullable=False)
    action = Column(String(20), nullable=False)       # GET, POST, PUT, DELETE
    resource = Column(String(100), nullable=False)     # e.g. "/api/pipelines"
    detail = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    risk_score = Column(Float, default=0.0)            # 0.0 – 1.0
    timestamp = Column(DateTime, server_default=func.now())
