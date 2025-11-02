from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession 
from app.db.models import User, File, Blob
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional
import hashlib
from pathlib import Path
from sqlalchemy.exc import SQLAlchemyError
from app.services.hashing import compute_digest_and_size

class UserRepository:
    def __init__(self,sesion: AsyncSession):
        self.session=sesion

    async def get_by_username(self, username:str):
        result = await self.session.execute(
            select(User).
            where(User.username == username)
            )
        return result.scalars().first()

    async def insert(self,sub:str, username:str, hashed_password:str) -> User:
        user= User(sub=sub, username=username, hashed_password=hashed_password)
        self.session.add(user)
        try:
            await self.session.commit()
            await self.session.refresh(user)
            return user
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e

class FileRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, file_id: int, owner_sub: str) -> Optional[File]:
        res = await self.session.execute(
            select(File)
            .options(selectinload(File.blob))
            .where(File.id == file_id, File.owner_sub == owner_sub))
        return res.scalars().first()
    

    async def create(self, owner_sub: str, display_name: Optional[str], blob_id: int) -> File:
        f = File(owner_sub=owner_sub, display_name=display_name, blob_id=blob_id)
        self.session.add(f)
        try:
            await self.session.commit()
            await self.session.refresh(f)
            return f
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e



    async def list_for_owner(self, owner_sub: str, limit: int = 50, offset: int = 0) -> list[File]:
        res = await self.session.execute(
            select(File)
            .options(selectinload(File.blob))
            .where(File.owner_sub == owner_sub)
            .order_by(File.id.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(res.scalars().all())



class BlobRepository:
    def __init__(self, session: AsyncSession, storage_path: Path):
        self.session = session
        self.storage_path = storage_path

    async def get_by_hash(self, digest: str) -> Blob | None:
        result = await self.session.execute(select(Blob).where(Blob.hash == digest))
        return result.scalars().first()





    #Put this into uploading service
    async def find_or_create(self, raw: bytes) -> tuple[Blob, bool, str, int]:
            digest, size_bytes = compute_digest_and_size(raw)
            # path = self.storage_path / digest

            result = await self.session.execute(select(Blob).where(Blob.hash == digest))
            return result.scalars().first()




            # result = await self.session.execute(select(Blob).where(Blob.hash == digest))
            # blob = result.scalars().first()
            # created = False

            # if not blob:
            #     path.parent.mkdir(parents=True, exist_ok=True)
            #     with open(path, "wb") as out:
            #         out.write(raw)

            #     blob = Blob(hash=digest, size_bytes=size_bytes)
            #     self.session.add(blob)

            #     try:
            #         await self.session.commit()
            #     except SQLAlchemyError:
            #         await self.session.rollback()
            #         raise
            #     created = True

            # return blob, created, digest, size_bytes
