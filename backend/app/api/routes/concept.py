"""
POST /generate/concept — submit a concept art generation job.
"""
from __future__ import annotations
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.models.schemas import ConceptArtRequest, ConceptArtResponse
from app.agents.concept_art_agent import ConceptArtAgent

router = APIRouter()
agent = ConceptArtAgent()

@router.post("/generate/concept", response_model=ConceptArtResponse)
async def generate_concept(request: ConceptArtRequest):
    response = agent.generate(request)
    return response
