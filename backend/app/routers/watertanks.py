"""
CityShield – Water Tanks Router
RESTful CRUD endpoints for water storage tank data
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas import WaterTankCreate, WaterTankUpdate, WaterTankOut
from app import crud
from security.rbac import require_role

router = APIRouter(prefix="/api/tanks", tags=["Water Tanks"])


@router.get("/", response_model=List[WaterTankOut])
def list_tanks(skip: int = 0, limit: int = 100,
               db: Session = Depends(get_db),
               _user=Depends(require_role(["admin", "operator", "viewer"]))):
    return crud.get_tanks(db, skip, limit)


@router.get("/{tank_id}", response_model=WaterTankOut)
def read_tank(tank_id: int,
              db: Session = Depends(get_db),
              _user=Depends(require_role(["admin", "operator", "viewer"]))):
    obj = crud.get_tank(db, tank_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Water tank not found")
    return obj


@router.post("/", response_model=WaterTankOut, status_code=201)
def create_tank(data: WaterTankCreate,
                db: Session = Depends(get_db),
                _user=Depends(require_role(["admin", "operator"]))):
    return crud.create_tank(db, data)


@router.put("/{tank_id}", response_model=WaterTankOut)
def update_tank(tank_id: int, data: WaterTankUpdate,
                db: Session = Depends(get_db),
                _user=Depends(require_role(["admin", "operator"]))):
    obj = crud.update_tank(db, tank_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="Water tank not found")
    return obj


@router.delete("/{tank_id}")
def delete_tank(tank_id: int,
                db: Session = Depends(get_db),
                _user=Depends(require_role(["admin"]))):
    if not crud.delete_tank(db, tank_id):
        raise HTTPException(status_code=404, detail="Water tank not found")
    return {"detail": "Water tank deleted"}
