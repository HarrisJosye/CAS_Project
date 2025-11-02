# app/services/uploading.py
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.db.models import Blob
from app.db.repositories import BlobRepository


async def ensure_blob(
    session: AsyncSession,
    storage_path: Path,
    digest: str,
    size_bytes: int,
    raw: bytes,
) -> tuple[Blob, bool]:
    """
    Ensure a blob exists in storage and DB.
    Returns (blob, created_new).
    """
    # Check if blob already exists in DB
    blobs = BlobRepository(session, storage_path)
    blob = await blobs.get_by_hash(digest)
    created = False


    if not blob:
        path = storage_path / digest
        path.parent.mkdir(parents=True, exist_ok=True)

        # Save file to storage
        with open(path, "wb") as out:
            out.write(raw)

        # Create DB record
        blob = Blob(hash=digest, size_bytes=size_bytes)
        session.add(blob)

        try:
            await session.commit()
        except SQLAlchemyError:
            await session.rollback()
            raise

        created = True

    return blob, created