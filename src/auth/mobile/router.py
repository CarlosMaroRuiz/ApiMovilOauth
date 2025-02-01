from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.config.get_db import get_db
from src.auth.dependencies import get_current_user
from . import schemas, service

router = APIRouter(prefix="/api/mobile", tags=["mobile"])
auth_service = service.MobileAuthService()

@router.post("/auth/google", response_model=schemas.AuthResponse)
async def mobile_google_auth(
    token_data: schemas.TokenData,
    db: Session = Depends(get_db)
):
    """Autenticación para apps móviles usando Google Sign-In"""
    try:
        # Verificar token de Google
        google_user = await auth_service.verify_google_token(token_data.id_token)
        
        # Obtener o crear usuario
        user = auth_service.get_user(db, google_user["email"])
        if not user:
            user = auth_service.create_user(
                db,
                email=google_user["email"],
                nombre=google_user.get("name")
            )
        
        # Crear tokens
        tokens = await auth_service.create_tokens({"email": user.correo})
        
        return {
            **tokens,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.correo,
                "name": google_user.get("name"),
                "picture": google_user.get("picture"),
                "created_at": user.fecha_creacion
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/auth/refresh", response_model=schemas.AuthResponse)
async def refresh_token(
    refresh_request: schemas.RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Renueva el token de acceso usando un refresh token"""
    try:
        # Verificar refresh token
        email = auth_service.verify_refresh_token(refresh_request.refresh_token)
        
        # Verificar que el usuario existe
        user = auth_service.get_user(db, email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Crear nuevos tokens
        tokens = await auth_service.create_tokens({"email": email})
        
        return {
            **tokens,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.correo,
                "name": None,
                "picture": None,
                "created_at": user.fecha_creacion
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

@router.get("/profile", response_model=schemas.UserResponse)
async def get_profile(
    current_user: dict = Depends(get_current_user)
):
    """Obtiene el perfil del usuario actual"""
    return current_user

@router.post("/logout")
async def logout(refresh_token: schemas.RefreshTokenRequest):
    """Endpoint para logout"""
    return {"message": "Logout successful"}