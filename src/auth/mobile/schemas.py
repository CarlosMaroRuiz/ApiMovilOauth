# src/auth/mobile/schemas.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class TokenData(BaseModel):
    id_token: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name: Optional[str] = None
    picture: Optional[str] = None
    created_at: datetime

class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: UserResponse

class TokenPayload(BaseModel):
    sub: EmailStr
    exp: Optional[int] = None
    refresh: Optional[bool] = False