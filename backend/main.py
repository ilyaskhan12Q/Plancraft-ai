"""
FastAPI main application entry point.
"""
from __future__ import annotations
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

load_dotenv()

RENDERS_DIR = os.getenv("RENDERS_DIR", "./renders")
UPLOADS_DIR = os.getenv("UPLOADS_DIR", "./uploads")

# Ensure directories exist
Path(RENDERS_DIR).mkdir(parents=True, exist_ok=True)
Path(UPLOADS_DIR).mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="AI Architect API",
    description="Generates 2D floor plans and 3D renders from natural language",
    version="1.0.0",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static files (rendered outputs) ──────────────────────────────────────────
app.mount("/renders", StaticFiles(directory=RENDERS_DIR), name="renders")

# ── Routes ────────────────────────────────────────────────────────────────────
from app.api.routes.generate import router as generate_router
from app.api.routes.status import router as status_router
from app.api.routes.upload import router as upload_router
from app.api.routes.export import router as export_router
from app.api.routes.customize import router as customize_router

app.include_router(generate_router)
app.include_router(status_router)
app.include_router(upload_router)
app.include_router(export_router)
app.include_router(customize_router)

from fastapi.responses import FileResponse

@app.get("/api/health")
async def health():
    return JSONResponse({
        "service": "AI Architect API",
        "status": "ok",
        "version": "1.0.0",
    })

@app.get("/{full_path:path}")
async def serve_flutter_app(full_path: str):
    web_dir = Path("../build/web")
    file_path = web_dir / full_path
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    index_file = web_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return JSONResponse({"error": "Frontend not built"}, status_code=404)
