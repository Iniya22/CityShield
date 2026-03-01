"""
CityShield – CRUD Operations
Reusable database query functions for all models
"""

from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func
from app import models, schemas
from datetime import datetime


# ── Pipelines ────────────────────────────────────────────────────────────────

def get_pipelines(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Pipeline).offset(skip).limit(limit).all()


def get_pipeline(db: Session, pipeline_id: int):
    return db.query(models.Pipeline).filter(models.Pipeline.id == pipeline_id).first()


def create_pipeline(db: Session, data: schemas.PipelineCreate):
    obj = models.Pipeline(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_pipeline(db: Session, pipeline_id: int, data: schemas.PipelineUpdate):
    obj = db.query(models.Pipeline).filter(models.Pipeline.id == pipeline_id).first()
    if not obj:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete_pipeline(db: Session, pipeline_id: int):
    obj = db.query(models.Pipeline).filter(models.Pipeline.id == pipeline_id).first()
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


# ── Water Tanks ──────────────────────────────────────────────────────────────

def get_tanks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.WaterTank).offset(skip).limit(limit).all()


def get_tank(db: Session, tank_id: int):
    return db.query(models.WaterTank).filter(models.WaterTank.id == tank_id).first()


def create_tank(db: Session, data: schemas.WaterTankCreate):
    obj = models.WaterTank(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_tank(db: Session, tank_id: int, data: schemas.WaterTankUpdate):
    obj = db.query(models.WaterTank).filter(models.WaterTank.id == tank_id).first()
    if not obj:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete_tank(db: Session, tank_id: int):
    obj = db.query(models.WaterTank).filter(models.WaterTank.id == tank_id).first()
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


# ── Maintenance Logs ─────────────────────────────────────────────────────────

def get_maintenance_logs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.MaintenanceLog).order_by(
        models.MaintenanceLog.created_at.desc()
    ).offset(skip).limit(limit).all()


def get_maintenance_log(db: Session, log_id: int):
    return db.query(models.MaintenanceLog).filter(
        models.MaintenanceLog.id == log_id
    ).first()


def create_maintenance_log(db: Session, data: schemas.MaintenanceCreate):
    obj = models.MaintenanceLog(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_maintenance_log(db: Session, log_id: int, data: schemas.MaintenanceUpdate):
    obj = db.query(models.MaintenanceLog).filter(
        models.MaintenanceLog.id == log_id
    ).first()
    if not obj:
        return None
    update_data = data.model_dump(exclude_unset=True)
    # Auto-set resolved_at when status changes to resolved
    if update_data.get("status") == "resolved" and obj.status != "resolved":
        update_data["resolved_at"] = datetime.utcnow()
    for key, value in update_data.items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete_maintenance_log(db: Session, log_id: int):
    obj = db.query(models.MaintenanceLog).filter(
        models.MaintenanceLog.id == log_id
    ).first()
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


# ── Audit Logs ───────────────────────────────────────────────────────────────

def get_audit_logs(db: Session, skip: int = 0, limit: int = 200):
    return db.query(models.AuditLog).order_by(
        models.AuditLog.timestamp.desc()
    ).offset(skip).limit(limit).all()


def create_audit_log(db: Session, user: str, action: str, resource: str,
                     detail: str = None, ip_address: str = None,
                     risk_score: float = 0.0):
    obj = models.AuditLog(
        user=user, action=action, resource=resource,
        detail=detail, ip_address=ip_address, risk_score=risk_score
    )
    db.add(obj)
    db.commit()
    return obj


# ── Dashboard Stats ──────────────────────────────────────────────────────────

def get_dashboard_stats(db: Session) -> dict:
    total_pipelines = db.query(models.Pipeline).count()
    total_tanks = db.query(models.WaterTank).count()
    active_pipelines = db.query(models.Pipeline).filter(
        models.Pipeline.status == "active"
    ).count()
    active_tanks = db.query(models.WaterTank).filter(
        models.WaterTank.status == "active"
    ).count()
    critical_assets = db.query(models.Pipeline).filter(
        models.Pipeline.status == "critical"
    ).count() + db.query(models.WaterTank).filter(
        models.WaterTank.status == "critical"
    ).count()
    open_maintenance = db.query(models.MaintenanceLog).filter(
        models.MaintenanceLog.status.in_(["open", "in_progress"])
    ).count()
    recent_audit = db.query(models.AuditLog).count()
    avg_level = db.query(sql_func.avg(models.WaterTank.current_level_pct)).scalar() or 0.0

    return {
        "total_pipelines": total_pipelines,
        "total_tanks": total_tanks,
        "active_pipelines": active_pipelines,
        "active_tanks": active_tanks,
        "critical_assets": critical_assets,
        "open_maintenance": open_maintenance,
        "recent_audit_events": recent_audit,
        "avg_tank_level": round(avg_level, 1)
    }
