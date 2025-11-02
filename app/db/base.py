from __future__ import annotations
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from app.db.models import Base



#putting async method for db side
_engine = create_async_engine('sqlite+aiosqlite:///./data/app.db', echo=False)
SessionLocal = async_sessionmaker(_engine, expire_on_commit=False)

async def init_db():
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

#asyncsession
@asynccontextmanager
# async def get_session() -> AsyncGenerator[AsyncSession, None]:
async def get_session():
    async with SessionLocal() as session:
        yield session
