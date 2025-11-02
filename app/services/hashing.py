# app/utils/hashing.py

import hashlib

def compute_digest_and_size(raw: bytes) -> tuple[str, int]:
    digest = hashlib.sha256(raw).hexdigest()
    size_bytes = len(raw)
    return digest, size_bytes