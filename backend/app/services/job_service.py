"""
Celery job service — the main pipeline:
Vision → Architect → Validator → Floor Plan → Script → Blender
"""
from __future__ import annotations
import json
import logging
import os
import uuid
from pathlib import Path
from typing import Optional

import redis
from celery import Celery
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
RENDERS_DIR = os.getenv("RENDERS_DIR", "./renders")
UPLOADS_DIR = os.getenv("UPLOADS_DIR", "./uploads")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")

# Celery app — concurrency=1 set in start_server.sh to avoid OOM
celery_app = Celery("ai_architect", broker=REDIS_URL, backend=REDIS_URL)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_expires=86400,
)

_redis = redis.from_url(REDIS_URL, decode_responses=True)

# ── Progress helpers ──────────────────────────────────────────────────────────

def update_progress(job_id: str, progress: float, stage: str) -> None:
    data = _redis.get(f"job:{job_id}")
    state = json.loads(data) if data else {}
    state.update({"status": "running", "progress": progress, "stage": stage})
    _redis.setex(f"job:{job_id}", 86400, json.dumps(state))
    logger.info("[%s] %.0f%% — %s", job_id, progress * 100, stage)


def set_job_state(job_id: str, **kwargs) -> None:
    """Alias kept for compatibility — merges kwargs into job state."""
    data = _redis.get(f"job:{job_id}")
    state = json.loads(data) if data else {}
    state.update(kwargs)
    _redis.setex(f"job:{job_id}", 86400, json.dumps(state))


def get_job_state(job_id: str) -> dict:
    data = _redis.get(f"job:{job_id}")
    if not data:
        return {"status": "not_found", "progress": 0.0, "stage": "Unknown"}
    return json.loads(data)


def create_job(job_id: str) -> None:
    state = {"job_id": job_id, "status": "pending", "progress": 0.0,
             "stage": "Queued", "variants": []}
    _redis.setex(f"job:{job_id}", 86400, json.dumps(state))


# ── Celery task ───────────────────────────────────────────────────────────────

@celery_app.task(name="run_pipeline", bind=True, max_retries=0)
def run_pipeline(self, job_id: str, request_json):
    """Main Celery pipeline task."""
    # Imports inside task to avoid worker import issues
    from app.models.schemas import GenerateRequest, BuildingSpec
    from app.agents.architect_agent import ArchitectAgent, DEFAULT_SPEC
    from app.agents.vision_agent import VisionAgent
    from app.agents.critique_agent import CritiqueAgent
    from app.blender.geometry_validator import validate_geometry
    from app.blender.floor_plan_renderer import render_floor_plan
    from app.blender.script_generator import generate_blender_script
    from app.blender.runner import run_blender_script
    from app.services.cost_estimator import estimate as estimate_cost

    # Deserialise request
    if isinstance(request_json, str):
        request_dict = json.loads(request_json)
    else:
        request_dict = request_json

    try:
        request = GenerateRequest.model_validate(request_dict)
    except Exception as exc:
        set_job_state(job_id, status="failed", stage="Validation error",
                      error=str(exc), progress=0.0)
        return

    job_dir = Path(RENDERS_DIR) / job_id
    floorplan_dir = job_dir / "floorplan"
    render_dir = job_dir / "render"
    job_dir.mkdir(parents=True, exist_ok=True)

    try:
        # ── Step 1: Vision analysis ──────────────────────────────────────────
        update_progress(job_id, 0.05, "Analysing uploaded photos…")
        site_analysis = None
        style_analysis = None
        uploads = Path(UPLOADS_DIR)

        vision = VisionAgent()
        if request.site_photo_key:
            p = uploads / request.site_photo_key
            if p.exists():
                site_analysis = vision.analyse_site(str(p))

        if request.style_photo_key:
            p = uploads / request.style_photo_key
            if p.exists():
                style_analysis = vision.analyse_style(str(p))

        # ── Step 2: Generate building spec ───────────────────────────────────
        update_progress(job_id, 0.10, "Designing building with AI…")
        architect = ArchitectAgent()
        spec: BuildingSpec = architect.generate(request, site_analysis, style_analysis)

        # ── Step 3: Geometry validation (max 2 fix attempts) ─────────────────
        update_progress(job_id, 0.25, "Validating geometry…")
        for attempt in range(2):
            errors = validate_geometry(spec)
            if not errors:
                break
            logger.warning("Geometry errors (attempt %d): %s", attempt, errors)
            spec = architect.generate(request, site_analysis, style_analysis,
                                      validation_errors=errors)
        else:
            errors = validate_geometry(spec)
            if errors:
                logger.warning("Geometry still invalid after retry — using default spec")
                spec = DEFAULT_SPEC
        # ── Step 3b: Cost estimate & design critique (non-blocking) ─────────────
        update_progress(job_id, 0.30, "Estimating construction cost…")
        try:
            cost_estimate = estimate_cost(spec).model_dump()
        except Exception as ce:
            logger.warning("Cost estimation failed: %s", ce)
            cost_estimate = {}

        update_progress(job_id, 0.32, "Generating architect's critique…")
        try:
            critique = CritiqueAgent().critique(spec, request)
        except Exception as cre:
            logger.warning("Critique agent failed: %s", cre)
            critique = []

        # ── Step 4: 2D floor plan (Preview + professional CAD) ───────────────
        update_progress(job_id, 0.35, "Rendering 2D floor plans (DXF/NanoCAD)…")
        from app.services.designer_service import DesignerService
        designer = DesignerService()
        design_results = designer.render_all(spec, str(floorplan_dir))
        fp_path = design_results.get("preview_png", "")
        dxf_path = design_results.get("cad_dxf", "")

        # ── Step 5: Generate Blender script ──────────────────────────────────
        update_progress(job_id, 0.45, "Generating 3D scene script…")
        render_dir.mkdir(parents=True, exist_ok=True)
        script = generate_blender_script(spec, str(render_dir))
        script_path = job_dir / "scene.py"
        script_path.write_text(script)

        # ── Step 6: Blender render ────────────────────────────────────────────
        update_progress(job_id, 0.50, "Rendering 3D exterior (this takes a few minutes)…")
        blender_result = run_blender_script(script, str(render_dir), "modern")

        # ── Build result URLs ──────────────────────────────────────────────────
        _base = os.getenv('BASE_URL', 'http://localhost:8080')
        base_export = f"{_base}/export/{job_id}"
        
        # Determine number of floors from generated files
        floor_plans = []
        dxfs = []
        if floorplan_dir.exists():
            for f in sorted(floorplan_dir.glob("floor_*.png")):
                idx = f.stem.split("_")[1]
                floor_plans.append(f"{base_export}/floorplan/{idx}")
            for f in sorted(floorplan_dir.glob("floor_*.dxf")):
                idx = f.stem.split("_")[1]
                dxfs.append(f"{base_export}/dxf/{idx}")

        variant = {
            "variant": "modern",
            "floorplan_url": floor_plans[0] if floor_plans else None,
            "floorplan_urls": floor_plans,
            "dxf_url": dxfs[0] if dxfs else None,
            "dxf_urls": dxfs,
            "render_url": f"{base_export}/render"
                          if blender_result.get("render_png") else None,
            "model_url": f"{base_export}/model"
                         if blender_result.get("model_glb") else None,
            "stl_url": f"{base_export}/stl"
                       if blender_result.get("model_stl") else None,
        }

        spec_dict = spec.model_dump()
        set_job_state(
            job_id,
            status="done",
            progress=1.0,
            stage="Complete",
            variants=[variant],
            spec=spec_dict,
            cost_estimate=cost_estimate,
            critique=critique,
        )
        logger.info("Job %s completed successfully", job_id)

    except Exception as exc:
        logger.exception("Pipeline failed for job %s", job_id)
        set_job_state(job_id, status="failed", stage="Pipeline error",
                      error=str(exc), progress=0.0)
