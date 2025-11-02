from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from app.db.base import get_session
from app.db.repositories import UserRepository
from sqlalchemy import select
import os
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(prefix="/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


@router.post("/token")
async def login(form: OAuth2PasswordRequestForm = Depends()):
# async def login(form: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_session)):
    async with get_session() as session:
        repo = UserRepository(session)
        user = await repo.get_by_username(form.username)

        if not user or not pwd_context.verify(form.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        now = datetime.now(timezone.utc)
        exp = now + timedelta(minutes=int(os.getenv('JWT_EXPIRE_MIN', '60')))
        payload = {
            "sub": user.sub,
            "username": user.username,
            "iss": os.getenv('JWT_ISSUER'),
            "aud": os.getenv('JWT_AUDIENCE'),
            "iat": int(now.timestamp()),
            "exp": int(exp.timestamp())
        }
        token = jwt.encode(payload, os.getenv('JWT_SECRET'), algorithm="HS256")
        return {"access_token": token, "token_type": "bearer"}


