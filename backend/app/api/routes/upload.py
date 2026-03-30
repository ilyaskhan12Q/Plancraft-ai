"""
POST /upload — accept image uploads.
Returns a key that can be used in GenerateRequest.
"""
from __future__ import annotations
import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

load_dotenv()
router = APIRouter()

UPLOADS_DIR = os.getenv("UPLOADS_DIR", "./uploads")
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only JPEG/PNG/WebP images allowed")

    data = await file.read()
    if len(data) > MAX_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 10 MB)")

    ext = Path(file.filename or "upload.jpg").suffix or ".jpg"
    key = f"{uuid.uuid4()}{ext}"

    out = Path(UPLOADS_DIR) / key
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)

    return JSONResponse({"key": key, "filename": file.filename})
