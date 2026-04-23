"""
Interior Design Agent — generates room-by-room interior design specifications
using Gemini. Returns furniture layouts, color schemes, material suggestions,
and lighting recommendations for each room.
"""
from __future__ import annotations
import json
import logging
import os
import re
from typing import List, Optional

from dotenv import load_dotenv
from google import genai

from app.models.schemas import (
    BuildingSpec, InteriorDesignRequest, InteriorRoomRequest,
    RoomInterior, InteriorDesignResponse,
)

load_dotenv()
logger = logging.getLogger(__name__)


def _extract_json(text: str) -> Optional[dict | list]:
    """Extract first valid JSON from text."""
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
    start = text.find("[")
    if start != -1:
        depth = 0
        for i, ch in enumerate(text[start:], start):
            if ch == "[": depth += 1
            elif ch == "]":
                depth -= 1
                if depth == 0:
                    try: return json.loads(text[start : i + 1])
                    except json.JSONDecodeError: break
    start = text.find("{")
    if start == -1: return None
    depth = 0
    for i, ch in enumerate(text[start:], start):
        if ch == "{": depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                try: return json.loads(text[start : i + 1])
                except json.JSONDecodeError: return None
    return None


class InteriorDesignAgent:
    """Generates AI-powered interior design recommendations per room."""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY", "")
        self._client = genai.Client(api_key=api_key)

    def generate_from_spec(
        self,
        spec: BuildingSpec,
        overall_style: str = "modern",
    ) -> InteriorDesignResponse:
        """Generate interior design for all rooms in a BuildingSpec."""
        rooms = []
        for fl in spec.floors:
            for rm in fl.rooms:
                rooms.append(InteriorRoomRequest(
                    name=rm.name,
                    style=overall_style,
                    width=rm.width,
                    depth=rm.depth,
                    floor=fl.floor_number,
                ))
        request = InteriorDesignRequest(rooms=rooms, overall_style=overall_style)
        return self.generate(request)

    def generate(self, request: InteriorDesignRequest) -> InteriorDesignResponse:
        """Generate interior design specs for the given rooms."""
        room_list = "\n".join(
            f"- {r.name} ({r.width:.1f}m × {r.depth:.1f}m, Floor {r.floor}) — Style: {r.style}"
            for r in request.rooms
        )

        prompt = f"""You are a world-class interior designer specializing in {request.overall_style} design.

Generate detailed interior design specifications for each room below.

## Rooms
{room_list}

## Instructions
For EACH room, provide:
1. **furniture**: List of furniture items with placement suggestions
2. **color_scheme**: Primary, secondary, and accent colors (hex codes)
3. **materials**: Wall, floor, and ceiling material recommendations
4. **lighting**: Types of lighting fixtures and placement
5. **decor_style**: A 1-sentence description of the interior mood
6. **estimated_budget_usd**: Rough furnishing budget in USD

## Response Format
Return ONLY a JSON array with one object per room:
[
  {{
    "room_name": "Living Room",
    "furniture": ["L-shaped sofa (center)", "Coffee table (oak)", "TV unit (wall-mounted)", "Bookshelf (corner)"],
    "color_scheme": {{"primary": "#F5F5F0", "secondary": "#2C3E50", "accent": "#E67E22"}},
    "materials": {{"walls": "matte white paint", "floor": "engineered oak", "ceiling": "white gypsum"}},
    "lighting": ["Recessed LED downlights (ceiling grid)", "Floor lamp (reading corner)", "LED strip (TV wall)"],
    "decor_style": "Warm Scandinavian minimalism with natural textures",
    "estimated_budget_usd": 3500
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
                logger.warning("No JSON found in interior design response")
                return InteriorDesignResponse(rooms=[], raw_response=text)

            if isinstance(raw, dict):
                raw = raw.get("rooms", [raw])
            if not isinstance(raw, list):
                raw = [raw]

            interiors = []
            for item in raw:
                try:
                    color_scheme = item.get("color_scheme", {})
                    materials = item.get("materials", {})
                    interiors.append(RoomInterior(
                        room_name=item.get("room_name", "Unknown"),
                        furniture=item.get("furniture", []),
                        color_scheme=color_scheme if isinstance(color_scheme, dict) else {},
                        materials=materials if isinstance(materials, dict) else {},
                        lighting=item.get("lighting", []),
                        decor_style=item.get("decor_style", ""),
                        estimated_budget_usd=item.get("estimated_budget_usd", 0),
                    ))
                except Exception as e:
                    logger.warning("Skipping invalid interior spec: %s", e)

            logger.info("Generated interior specs for %d rooms", len(interiors))
            return InteriorDesignResponse(rooms=interiors, raw_response=text)

        except Exception as exc:
            logger.error("Interior design generation failed: %s", exc)
            return InteriorDesignResponse(rooms=[], raw_response=str(exc))
