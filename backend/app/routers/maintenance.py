"""
CityShield – Maintenance Router
RESTful CRUD endpoints for maintenance logs
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas import MaintenanceCreate, MaintenanceUpdate, MaintenanceOut
from app import crud
from security.rbac import require_role

router = APIRouter(prefix="/api/maintenance", tags=["Maintenance"])


@router.get("/", response_model=List[MaintenanceOut])
def list_logs(skip: int = 0, limit: int = 100,
              db: Session = Depends(get_db),
              _user=Depends(require_role(["admin", "operator", "viewer"]))):
    return crud.get_maintenance_logs(db, skip, limit)


@router.get("/{log_id}", response_model=MaintenanceOut)
def read_log(log_id: int,
             db: Session = Depends(get_db),
             _user=Depends(require_role(["admin", "operator", "viewer"]))):
    obj = crud.get_maintenance_log(db, log_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Maintenance log not found")
    return obj


@router.post("/", response_model=MaintenanceOut, status_code=201)
def create_log(data: MaintenanceCreate,
               db: Session = Depends(get_db),
               _user=Depends(require_role(["admin", "operator"]))):
    return crud.create_maintenance_log(db, data)


@router.put("/{log_id}", response_model=MaintenanceOut)
def update_log(log_id: int, data: MaintenanceUpdate,
               db: Session = Depends(get_db),
               _user=Depends(require_role(["admin", "operator"]))):
    obj = crud.update_maintenance_log(db, log_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="Maintenance log not found")
    return obj


@router.delete("/{log_id}")
def delete_log(log_id: int,
               db: Session = Depends(get_db),
               _user=Depends(require_role(["admin"]))):
    if not crud.delete_maintenance_log(db, log_id):
        raise HTTPException(status_code=404, detail="Maintenance log not found")
    return {"detail": "Maintenance log deleted"}
