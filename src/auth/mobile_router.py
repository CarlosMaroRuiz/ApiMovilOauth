from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer
from sqlalchemy.orm import Session

from .web import schemas
from .web import service
from src.config.database import SessionLocal

router = APIRouter(prefix="/api/mobile")

@router.post("/auth/google")
async def mobile_google_auth(id_token: str, db: Session = Depends(get_db)):
    """
    Endpoint para autenticación desde app móvil usando Google Sign-In
    El id_token viene del SDK de Google en el móvil
    """
    try:
        # Verificar el token de Google
        user_data = await service.verify_google_token(id_token)
        
        # Crear o actualizar usuario
        user = service.get_user_by_email(db, user_data["email"])
        if not user:
            user = service.create_user(db, schemas.UsuarioCreate(
                correo=user_data["email"],
                contraseña="mobile_auth"
            ))
        
        # Generar token JWT
        token = await service.create_token({"sub": user.correo})
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "email": user.correo,
                "id": user.id
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/auth/refresh")
async def refresh_token(current_token: str = Depends(service.verify_token)):
    """
    Endpoint para renovar el token desde la app móvil
    """
    try:
        new_token = await service.create_token({"sub": current_token})
        return {"access_token": new_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))