"""
GET /status/{job_id} — poll job progress.
"""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.services.job_service import get_job_state

router = APIRouter()


@router.get("/status/{job_id}")
async def status(job_id: str):
    state = get_job_state(job_id)
    if state.get("status") == "not_found":
        raise HTTPException(status_code=404, detail="Job not found")
    return state
