"""
POST /customize/{job_id} — apply material/colour/roof overrides and re-render.
"""
from __future__ import annotations
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.models.schemas import CustomizeRequest
from app.services.job_service import get_job_state, run_pipeline, create_job
import uuid

load_dotenv()
router = APIRouter()

RENDERS_DIR = os.getenv("RENDERS_DIR", "./renders")


@router.post("/customize/{job_id}")
async def customize(job_id: str, req: CustomizeRequest):
    state = get_job_state(job_id)
    if state.get("status") not in ("done",):
        raise HTTPException(status_code=400, detail="Job must be in 'done' state to customise")

    spec_dict = state.get("spec")
    if not spec_dict:
        raise HTTPException(status_code=404, detail="No spec found for job")

    # Apply overrides
    if req.exterior_color:
        spec_dict["exterior_color"] = req.exterior_color
    if req.roof_color:
        spec_dict["roof_color"] = req.roof_color
    if req.roof_type:
        spec_dict["roof_type"] = req.roof_type
    if req.facade_material:
        spec_dict["facade_material"] = req.facade_material
    if req.window_type:
        spec_dict["window_type"] = req.window_type

    # Generate a new child job for the customised render
    new_job_id = f"{job_id}_custom_{uuid.uuid4().hex[:6]}"

    # We create a minimal re-render task by saving the updated spec to Redis
    # and scheduling a render-only pipeline
    from app.models.schemas import BuildingSpec
    from app.blender.script_generator import generate_blender_script
    from app.blender.runner import run_blender_script
    from app.blender.floor_plan_renderer import render_floor_plan

    spec = BuildingSpec.model_validate(spec_dict)
    render_dir = Path(RENDERS_DIR) / new_job_id / "render"
    fp_dir = Path(RENDERS_DIR) / new_job_id / "floorplan"

    render_floor_plan(spec, str(fp_dir))
    script = generate_blender_script(spec, str(render_dir))
    run_blender_script(script, str(render_dir), "custom")

    _base = os.getenv("BASE_URL", "http://localhost:8080")
    return JSONResponse({
        "new_job_id": new_job_id,
        "floorplan_url": f"{_base}/export/{new_job_id}/floorplan",
        "render_url": f"{_base}/export/{new_job_id}/render",
        "model_url": f"{_base}/export/{new_job_id}/model",
        "stl_url": f"{_base}/export/{new_job_id}/stl",
    })
