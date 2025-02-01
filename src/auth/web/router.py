# src/auth/web/router.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session

from src.config.get_db import get_db
from src.auth.dependencies import get_current_user
from . import schemas, service

router = APIRouter(tags=["auth"])
auth_service = service.WebAuthService()

@router.get("/login/google", response_model=schemas.GoogleAuthURL)
async def login_google(request: Request):
    """Inicia el flujo de autenticación con Google"""
    auth_url = auth_service.get_google_auth_url()
    print(auth_url)
    return {"url": auth_url}

@router.get("/auth/callback")
async def auth_callback(
    code: str,
    db: Session = Depends(get_db)
):
    """Maneja la respuesta de Google después de la autenticación"""
    try:
        # Intercambiar código por token
        token_data = await auth_service.exchange_code_for_token(code)
        access_token = token_data.get("access_token")
        # Obtener información del usuario
        print(access_token)
        user_info = await auth_service.get_google_user_info(access_token)
        print(user_info)
        # Buscar o crear usuario
        user = auth_service.get_user(db, user_info["email"])
        if not user:
            print("usuario nuevo")
            user = auth_service.create_user(
                db,
                email=user_info["email"]
            )
        
        
        # Crear token JWT
        token = await auth_service.create_access_token({"sub": user.correo})
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.correo,
                "name": user_info.get("name"),
                "picture": user_info.get("picture"),
                "created_at": user.fecha_creacion
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/me", response_model=schemas.UserResponse)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """Obtiene la información del usuario actual"""
    return current_user

@router.post("/logout")
async def logout():
    """Cierra la sesión del usuario"""
    response = JSONResponse(content={"message": "Successfully logged out"})
    response.delete_cookie("Authorization")
    return response