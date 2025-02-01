# src/auth/mobile/service.py
from datetime import datetime, timedelta
from typing import Optional
import httpx
from fastapi import HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from src.config.settings import settings
from src.auth.models import Usuario
from . import schemas

class MobileAuthService:
    @staticmethod
    async def verify_google_token(id_token: str) -> dict:
        """Verifica el token de Google recibido desde la app móvil"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
            )
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Google token"
                )
            return response.json()

    @staticmethod
    async def create_tokens(user_data: dict) -> dict:
        """Crea tokens de acceso y refresh"""
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=30)
        
        to_encode = {"sub": user_data["email"]}
        
        # Crear access token
        access_expire = datetime.utcnow() + access_token_expires
        to_encode.update({"exp": access_expire})
        access_token = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
        
        # Crear refresh token
        refresh_expire = datetime.utcnow() + refresh_token_expires
        to_encode.update({"exp": refresh_expire, "refresh": True})
        refresh_token = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": access_token_expires.seconds
        }

    @staticmethod
    def verify_refresh_token(refresh_token: str) -> str:
        """Verifica el refresh token y retorna el email del usuario"""
        try:
            payload = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            if not payload.get("refresh"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
            email: str = payload.get("sub")
            if email is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token data"
                )
            return email
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate refresh token"
            )

    @staticmethod
    def get_user(db: Session, email: str) -> Optional[Usuario]:
        """Obtiene un usuario por su email"""
        return db.query(Usuario).filter(Usuario.correo == email).first()

    @staticmethod
    def create_user(db: Session, email: str, nombre: Optional[str] = None) -> Usuario:
        """Crea un nuevo usuario"""
        db_user = Usuario(
            correo=email,
            contraseña="mobile_auth",
            nombre=nombre
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user