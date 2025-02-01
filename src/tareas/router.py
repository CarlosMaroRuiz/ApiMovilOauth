# src/tareas/router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from src.config.get_db import get_db
from src.auth.dependencies import get_current_user
from . import schemas, service

router = APIRouter(prefix="/tareas", tags=["tareas"])
tareas_service = service.TareasService()

@router.get("/", response_model=List[schemas.Tarea])
def get_tareas(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return tareas_service.get_tareas(db, current_user["id"])

@router.post("/", response_model=schemas.Tarea)
def create_tarea(
    tarea: schemas.TareaCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return tareas_service.create_tarea(db, tarea, current_user["id"])

@router.get("/{tarea_id}", response_model=schemas.Tarea)
def get_tarea(
    tarea_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return tareas_service.get_tarea(db, tarea_id, current_user["id"])

@router.put("/{tarea_id}", response_model=schemas.Tarea)
def update_tarea(
    tarea_id: int,
    tarea: schemas.TareaCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return tareas_service.update_tarea(db, tarea_id, tarea, current_user["id"])

@router.delete("/{tarea_id}")
def delete_tarea(
    tarea_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return tareas_service.delete_tarea(db, tarea_id, current_user["id"])