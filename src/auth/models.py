from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from sqlalchemy.orm import relationship
from src.config.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    correo = Column(String, unique=True, index=True)
    contraseña = Column(String)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    # Relación con Tareas
    tareas = relationship("Tarea", back_populates="usuario", cascade="all, delete-orphan")
