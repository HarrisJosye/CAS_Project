from fastapi import APIRouter, UploadFile, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from jose import jwt, JWTError
from app.db.base import get_session
from app.db.repositories import FileRepository
from app.services.hashing import compute_digest_and_size
from app.services.uploading import ensure_blob

import os
from pathlib import Path

router = APIRouter(prefix="/files", tags=["files"])
STORAGE = Path("data/blobs")
STORAGE.mkdir(parents=True, exist_ok=True)


async def get_current_user(request: Request):
    auth = request.headers.get("Authorization")
    if not auth or not auth.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = auth.split()[1]
    try:
        payload = jwt.decode(
            token,
            os.getenv("JWT_SECRET"),
            algorithms=["HS256"],
            audience=os.getenv("JWT_AUDIENCE"),
            issuer=os.getenv("JWT_ISSUER"),
        )
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")



@router.post("")
async def upload_file(file: UploadFile, user=Depends(get_current_user)):
    raw = await file.read()

    async with get_session() as session:
        # blob_repo = BlobRepository(session, STORAGE)
        # blob, created, digest, size_bytes = await blob_repo.find_or_create(raw)

        digest, size_bytes = compute_digest_and_size(raw)
        blob, created = await ensure_blob(session, STORAGE, digest, size_bytes, raw)


        file_repo=FileRepository(session)
        file_record =await file_repo.create(owner_sub=user["sub"], display_name=file.filename, blob_id=blob.id)

        return {
            "file_id": file_record.id,
            "hash": digest,
            "size_bytes": size_bytes,
            "deduped": not created,
        }


@router.get("")
async def list_files(user=Depends(get_current_user)):
    async with get_session() as session:

        repo = FileRepository(session)
        files = await repo.list_for_owner(owner_sub=user["sub"])

        # Process from oldest -> newest so that the *first* per-hash is not deduped
        rows_sorted = sorted(files, key=lambda f: f.id)
        seen: dict[str, int] = {}
        items = []
        for r in rows_sorted:
            count = seen.get(r.blob.hash, 0)
            deduped = count >= 1
            seen[r.blob.hash] = count + 1
            items.append({
                "id": r.id,
                "name": r.display_name,
                "hash": r.blob.hash,
                "size_bytes": r.blob.size_bytes,
                "deduped": deduped,
            })

        # Return newest first in the UI
        items.sort(key=lambda it: it["id"], reverse=True)
        return items


@router.get("/{file_id}/download")
async def download_file(file_id: int, user=Depends(get_current_user)):
    async with get_session() as session:

        repo = FileRepository(session)
        f = await repo.get(file_id=file_id,owner_sub=user["sub"])

        if not f:
            raise HTTPException(status_code=404)

        return FileResponse(STORAGE / f.blob.hash, filename=f.display_name)
