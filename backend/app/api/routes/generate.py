"""
POST /generate — submit a generation job.
"""
from __future__ import annotations
import json
import uuid

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.models.schemas import GenerateRequest
from app.services.job_service import celery_app, create_job, run_pipeline

router = APIRouter()


@router.post("/generate")
async def generate(request: GenerateRequest):
    job_id = str(uuid.uuid4())
    create_job(job_id)
    request_json = request.model_dump_json()
    run_pipeline.apply_async(
        args=[job_id, request_json],
        task_id=job_id,
    )
    return JSONResponse({"job_id": job_id})
