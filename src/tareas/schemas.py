# src/tareas/schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TareaBase(BaseModel):
    titulo: str
    descripcion: Optional[str] = None

class TareaCreate(TareaBase):
    pass

class Tarea(TareaBase):
    id: int
    usuario_id: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True