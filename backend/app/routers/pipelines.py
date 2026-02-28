"""
CityShield – Pipelines Router
RESTful CRUD endpoints for water supply pipeline data
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas import PipelineCreate, PipelineUpdate, PipelineOut
from app import crud
from security.rbac import require_role

router = APIRouter(prefix="/api/pipelines", tags=["Pipelines"])


@router.get("/", response_model=List[PipelineOut])
def list_pipelines(skip: int = 0, limit: int = 100,
                   db: Session = Depends(get_db),
                   _user=Depends(require_role(["admin", "operator", "viewer"]))):
    return crud.get_pipelines(db, skip, limit)


@router.get("/{pipeline_id}", response_model=PipelineOut)
def read_pipeline(pipeline_id: int,
                  db: Session = Depends(get_db),
                  _user=Depends(require_role(["admin", "operator", "viewer"]))):
    obj = crud.get_pipeline(db, pipeline_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return obj


@router.post("/", response_model=PipelineOut, status_code=201)
def create_pipeline(data: PipelineCreate,
                    db: Session = Depends(get_db),
                    _user=Depends(require_role(["admin", "operator"]))):
    return crud.create_pipeline(db, data)


@router.put("/{pipeline_id}", response_model=PipelineOut)
def update_pipeline(pipeline_id: int, data: PipelineUpdate,
                    db: Session = Depends(get_db),
                    _user=Depends(require_role(["admin", "operator"]))):
    obj = crud.update_pipeline(db, pipeline_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return obj


@router.delete("/{pipeline_id}")
def delete_pipeline(pipeline_id: int,
                    db: Session = Depends(get_db),
                    _user=Depends(require_role(["admin"]))):
    if not crud.delete_pipeline(db, pipeline_id):
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return {"detail": "Pipeline deleted"}
