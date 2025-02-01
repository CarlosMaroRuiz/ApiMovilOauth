# src/auth/web/service.py
from datetime import datetime, timedelta
import httpx
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from src.config.settings import settings
from src.auth.models import Usuario

class WebAuthService:
    def __init__(self):
        self.google_client_id = settings.GOOGLE_CLIENT_ID
        self.google_client_secret = settings.GOOGLE_CLIENT_SECRET
        self.google_redirect_uri = settings.GOOGLE_REDIRECT_URI  

    def get_google_auth_url(self, state: str = None) -> str:
        """Genera la URL de autenticación de Google"""
        base_url = "https://accounts.google.com/o/oauth2/v2/auth"
        params = {
            "client_id": self.google_client_id,
            "response_type": "code",
            "scope": "openid email profile",
            "redirect_uri": self.google_redirect_uri,
            "access_type": "offline",
            "prompt": "consent"
        }
        print(self.google_redirect_uri)
      
        if state:
            params["state"] = state
            
        query_params = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{base_url}?{query_params}"

    async def exchange_code_for_token(self, code: str) -> dict:
        """Intercambia el código de autorización por tokens de Google"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": self.google_client_id,
                    "client_secret": self.google_client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.google_redirect_uri
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange code for token"
                )
                
            return response.json()

    async def get_google_user_info(self, access_token: str) -> dict:
        """Obtiene la información del usuario de Google"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to get user info"
                )
                
            return response.json()

    async def create_access_token(self, data: dict) -> str:
        """Crea un token JWT para el usuario"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        
        return jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

    @staticmethod
    def get_user(db: Session, email: str) -> Usuario:
        """Obtiene un usuario por su email"""
        try:
            db.query(Usuario).filter(Usuario.correo == email).first()
        except Exception as e:
            print(e)
            return None

    @staticmethod
    def create_user(db: Session, email: str) -> Usuario:
        """Crea un nuevo usuario"""
        db_user = Usuario(
            correo=email,
            contraseña="google_auth",  #
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user