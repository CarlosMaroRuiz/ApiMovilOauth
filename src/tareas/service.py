# src/tareas/service.py
from sqlalchemy.orm import Session
from . import models, schemas
from fastapi import HTTPException

class TareasService:
    @staticmethod
    def get_tareas(db: Session, usuario_id: int):
        return db.query(models.Tarea).filter(models.Tarea.usuario_id == usuario_id).all()

    @staticmethod
    def create_tarea(db: Session, tarea: schemas.TareaCreate, usuario_id: int):
        db_tarea = models.Tarea(
            titulo=tarea.titulo,
            descripcion=tarea.descripcion,
            usuario_id=usuario_id
        )
        db.add(db_tarea)
        db.commit()
        db.refresh(db_tarea)
        return db_tarea

    @staticmethod
    def get_tarea(db: Session, tarea_id: int, usuario_id: int):
        tarea = db.query(models.Tarea).filter(
            models.Tarea.id == tarea_id,
            models.Tarea.usuario_id == usuario_id
        ).first()
        if not tarea:
            raise HTTPException(status_code=404, detail="Tarea no encontrada")
        return tarea

    @staticmethod
    def update_tarea(db: Session, tarea_id: int, tarea: schemas.TareaCreate, usuario_id: int):
        db_tarea = TareasService.get_tarea(db, tarea_id, usuario_id)
        db_tarea.titulo = tarea.titulo
        db_tarea.descripcion = tarea.descripcion
        db.commit()
        db.refresh(db_tarea)
        return db_tarea

    @staticmethod
    def delete_tarea(db: Session, tarea_id: int, usuario_id: int):
        db_tarea = TareasService.get_tarea(db, tarea_id, usuario_id)
        db.delete(db_tarea)
        db.commit()
        return {"message": "Tarea eliminada"}