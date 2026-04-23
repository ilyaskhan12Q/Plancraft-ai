"""
Concept Art Agent — generates multiple AI-powered architectural concept descriptions
using Gemini. Returns structured mood boards with style details, color palettes,
and architectural feature lists for client visualization.
"""
from __future__ import annotations
import json
import logging
import os
import re
from typing import List, Optional

from dotenv import load_dotenv
from google import genai

from app.models.schemas import ConceptArtRequest, ConceptIdea, ConceptArtResponse

load_dotenv()
logger = logging.getLogger(__name__)


def _extract_json(text: str) -> Optional[dict | list]:
    """Extract first valid JSON array or object from text."""
    # Try code block first
    m = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass

    # Try finding a JSON array
    start = text.find("[")
    if start != -1:
        depth = 0
        for i, ch in enumerate(text[start:], start):
            if ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start : i + 1])
                    except json.JSONDecodeError:
                        break

    # Fall back to object
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    for i, ch in enumerate(text[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start : i + 1])
                except json.JSONDecodeError:
                    return None
    return None


class ConceptArtAgent:
    """Generates multiple architectural concept ideas from a design brief."""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY", "")
        self._client = genai.Client(api_key=api_key)

    def generate(self, request: ConceptArtRequest) -> ConceptArtResponse:
        """Generate 4-5 concept art descriptions based on the request."""
        inspirations = ", ".join(request.inspirations) if request.inspirations else "contemporary masters"
        num = request.num_concepts or 5

        prompt = f"""You are a world-class architectural concept artist and mood board designer.

Generate exactly {num} unique architectural concept ideas based on this brief:

## Design Brief
- Style: {request.style}
- Description: {request.description}
- Architectural Inspirations: {inspirations}
- Mood: {request.mood or 'Not specified'}
- Building Type: {request.building_type or 'residential'}

## Instructions
For each concept, provide:
1. A creative concept name
2. A vivid 2-3 sentence description of the building's appearance
3. Key architectural features (list of 4-6 features)
4. A color palette (list of 4-5 hex colors)
5. Recommended materials (list of 3-4 materials)
6. A photorealistic render prompt that could be used with an image AI

## Response Format
Return ONLY a JSON array of {num} objects:
[
  {{
    "name": "Concept Name",
    "description": "Vivid description...",
    "features": ["feature1", "feature2", ...],
    "color_palette": ["#hex1", "#hex2", ...],
    "materials": ["material1", "material2", ...],
    "render_prompt": "A photorealistic architectural render of..."
  }}
]
"""
        try:
            response = self._client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            text = response.text or ""
            raw = _extract_json(text)

            if raw is None:
                logger.warning("No JSON found in concept art response")
                return ConceptArtResponse(concepts=[], raw_response=text)

            # Handle both array and object responses
            if isinstance(raw, dict):
                raw = raw.get("concepts", [raw])
            if not isinstance(raw, list):
                raw = [raw]

            concepts = []
            for item in raw[:num]:
                try:
                    concepts.append(ConceptIdea(
                        name=item.get("name", "Unnamed Concept"),
                        description=item.get("description", ""),
                        features=item.get("features", []),
                        color_palette=item.get("color_palette", []),
                        materials=item.get("materials", []),
                        render_prompt=item.get("render_prompt", ""),
                    ))
                except Exception as e:
                    logger.warning("Skipping invalid concept: %s", e)

            logger.info("Generated %d concept ideas", len(concepts))
            return ConceptArtResponse(concepts=concepts, raw_response=text)

        except Exception as exc:
            logger.error("Concept art generation failed: %s", exc)
            return ConceptArtResponse(concepts=[], raw_response=str(exc))
