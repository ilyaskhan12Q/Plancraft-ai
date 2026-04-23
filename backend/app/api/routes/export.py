"""
Export routes — serve rendered files.
GET /export/{job_id}/floorplan  → 2D floor plan PNG
GET /export/{job_id}/render     → 3D render PNG
GET /export/{job_id}/model      → GLB 3D model
GET /export/{job_id}/stl        → STL for 3D printing
GET /export/{job_id}/cost-report→ Cost estimation report (JSON)
GET /export/{job_id}/critique   → Design critique report (JSON)
GET /export/{job_id}/interior   → Interior design report (JSON)
GET /export/{job_id}/materials  → Material optimization report (JSON)
GET /export/{job_id}/links      → JSON with all URLs
"""
from __future__ import annotations
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse

load_dotenv()
router = APIRouter()

RENDERS_DIR = os.getenv("RENDERS_DIR", "./renders")


def _base_url() -> str:
    return os.getenv("BASE_URL", "http://localhost:8080")


def _job_dir(job_id: str) -> Path:
    return Path(RENDERS_DIR) / job_id


def _require(path: Path) -> Path:
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not yet available")
    return path


@router.get("/export/{job_id}/floorplan")
async def export_floorplan(job_id: str):
    p = _require(_job_dir(job_id) / "floorplan" / "floor_plan.png")
    return FileResponse(str(p), media_type="image/png",
                        filename=f"floorplan_{job_id}.png")


@router.get("/export/{job_id}/render")
async def export_render(job_id: str):
    p = _require(_job_dir(job_id) / "render" / "render.png")
    return FileResponse(str(p), media_type="image/png",
                        filename=f"render_{job_id}.png")


@router.get("/export/{job_id}/model")
async def export_model(job_id: str):
    p = _require(_job_dir(job_id) / "render" / "model.glb")
    return FileResponse(str(p), media_type="model/gltf-binary",
                        filename=f"model_{job_id}.glb")


@router.get("/export/{job_id}/stl")
async def export_stl(job_id: str):
    p = _require(_job_dir(job_id) / "render" / "model.stl")
    return FileResponse(str(p), media_type="model/stl",
                        filename=f"model_{job_id}.stl")


@router.get("/export/{job_id}/dxf")
async def export_dxf(job_id: str):
    p = _require(_job_dir(job_id) / "floorplan" / "floor_plan.dxf")
    return FileResponse(str(p), media_type="application/dxf",
                        filename=f"floor_plan_{job_id}.dxf")


@router.get("/export/{job_id}/cost-report")
async def export_cost_report(job_id: str):
    p = _require(_job_dir(job_id) / "cost_report.json")
    return FileResponse(str(p), media_type="application/json")


@router.get("/export/{job_id}/critique")
async def export_critique(job_id: str):
    p = _require(_job_dir(job_id) / "critique.json")
    return FileResponse(str(p), media_type="application/json")


@router.get("/export/{job_id}/interior")
async def export_interior(job_id: str):
    p = _require(_job_dir(job_id) / "interior.json")
    return FileResponse(str(p), media_type="application/json")


@router.get("/export/{job_id}/materials")
async def export_materials(job_id: str):
    p = _require(_job_dir(job_id) / "materials.json")
    return FileResponse(str(p), media_type="application/json")


@router.get("/export/{job_id}/links")
async def export_links(job_id: str):
    base = f"{_base_url()}/export/{job_id}"
    jd = _job_dir(job_id)
    return JSONResponse({
        "job_id": job_id,
        "floorplan": f"{base}/floorplan" if (jd / "floorplan" / "floor_plan.png").exists() else None,
        "render": f"{base}/render" if (jd / "render" / "render.png").exists() else None,
        "model": f"{base}/model" if (jd / "render" / "model.glb").exists() else None,
        "stl": f"{base}/stl" if (jd / "render" / "model.stl").exists() else None,
        "dxf": f"{base}/dxf" if (jd / "floorplan" / "floor_plan.dxf").exists() else None,
        "cost_report": f"{base}/cost-report" if (jd / "cost_report.json").exists() else None,
        "critique": f"{base}/critique" if (jd / "critique.json").exists() else None,
        "interior": f"{base}/interior" if (jd / "interior.json").exists() else None,
        "materials": f"{base}/materials" if (jd / "materials.json").exists() else None,
    })
