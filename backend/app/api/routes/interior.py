"""
POST /generate/interior — submit an interior design generation job.
"""
from __future__ import annotations
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.models.schemas import InteriorDesignRequest, InteriorDesignResponse
from app.agents.interior_agent import InteriorDesignAgent

router = APIRouter()
agent = InteriorDesignAgent()

@router.post("/generate/interior", response_model=InteriorDesignResponse)
async def generate_interior(request: InteriorDesignRequest):
    response = agent.generate(request)
    return response
