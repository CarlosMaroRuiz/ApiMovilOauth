# src/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config.database import engine, Base
from src.auth.web.router import router as router_web
from src.auth.mobile.router import router as router_mobile
from src.tareas.router import router as router_tareas

# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Tareas",
    description="API para gestión de tareas con autenticación web y móvil",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas
app.include_router(router_web, prefix="/api")
app.include_router(router_mobile) 
app.include_router(router_tareas, prefix="/api")
# uvicorn src.main:app --reload --host 0.0.0.0 --port 3000