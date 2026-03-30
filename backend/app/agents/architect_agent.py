"""
Gemini 2.5 Flash architect agent.
Uses google-genai SDK (not deprecated google-generativeai).
"""
from __future__ import annotations
import json
import logging
import os
import re
from typing import Optional

from dotenv import load_dotenv
from google import genai

from app.models.schemas import (
    BuildingSpec, CameraSpec, FloorSpec, GenerateRequest, RoomSpec,
    SiteAnalysis, StyleAnalysis,
)

load_dotenv()
logger = logging.getLogger(__name__)

# ─────────────────────────── Default Spec ────────────────────────────────────

DEFAULT_SPEC = BuildingSpec(
    style="modern",
    exterior_color="#F5F5F0",
    roof_type="flat",
    roof_color="#555555",
    window_type="casement",
    door_style="modern_panel",
    facade_material="plaster",
    camera=CameraSpec(pos=[20.0, -20.0, 15.0], look_at=[0.0, 0.0, 3.0], lens=35.0),
    floors=[
        FloorSpec(
            floor_number=0,
            height=3.0,
            rooms=[
                RoomSpec(name="Living Room", width=5.0, depth=4.0, x=0.0, y=0.0,
                         floor=0, has_window=True, has_door=True, door_wall="south"),
                RoomSpec(name="Kitchen",     width=3.0, depth=3.0, x=5.0, y=0.0,
                         floor=0, has_window=True, has_door=False, door_wall="south"),
                RoomSpec(name="Dining",      width=3.0, depth=3.0, x=5.0, y=3.0,
                         floor=0, has_window=True, has_door=False, door_wall="east"),
                RoomSpec(name="Bathroom",    width=2.0, depth=2.0, x=3.0, y=4.0,
                         floor=0, has_window=False, has_door=True, door_wall="south"),
            ],
        ),
        FloorSpec(
            floor_number=1,
            height=3.0,
            rooms=[
                RoomSpec(name="Master Bedroom", width=4.0, depth=4.0, x=0.0, y=0.0,
                         floor=1, has_window=True, has_door=True, door_wall="south"),
                RoomSpec(name="Bedroom 2",      width=3.5, depth=3.5, x=4.0, y=0.0,
                         floor=1, has_window=True, has_door=True, door_wall="south"),
                RoomSpec(name="Bedroom 3",      width=3.5, depth=3.5, x=4.0, y=3.5,
                         floor=1, has_window=True, has_door=True, door_wall="north"),
                RoomSpec(name="Bathroom",       width=2.0, depth=2.0, x=0.0, y=4.0,
                         floor=1, has_window=False, has_door=True, door_wall="east"),
            ],
        ),
    ],
)

# ─────────────────────────── Schema Snippet ───────────────────────────────────

_SCHEMA_HINT = """
{
  "style": "modern",
  "exterior_color": "#RRGGBB",
  "roof_type": "flat|gable|hip|shed|mansard",
  "roof_color": "#RRGGBB",
  "window_type": "casement|sliding|fixed|bay",
  "door_style": "string",
  "facade_material": "plaster|brick|concrete|wood|stone",
  "camera": {
    "pos": [x, y, z],
    "look_at": [x, y, z],
    "lens": 35.0
  },
  "floors": [
    {
      "floor_number": 0,
      "height": 3.0,
      "rooms": [
        {
          "name": "Living Room",
          "width": 5.0,
          "depth": 4.0,
          "x": 0.0,
          "y": 0.0,
          "floor": 0,
          "has_window": true,
          "has_door": true,
          "door_wall": "south"
        }
      ]
    }
  ]
}
"""

# ─────────────────────────── Prompt Builder ──────────────────────────────────

def _build_prompt(
    request: GenerateRequest,
    site: Optional[SiteAnalysis],
    style_ref: Optional[StyleAnalysis],
    validation_errors: Optional[list[str]] = None,
) -> str:
    plot = request.plot
    rms = request.rooms

    ctx = f"""You are a professional architect. Generate a complete building design spec.

## Project Brief
- Plot: {plot.length}m × {plot.width}m, {plot.floors} floor(s), facing {plot.orientation}
- Rooms: {rms.bedrooms} bedrooms, {rms.bathrooms} bathrooms,
  living={rms.living_room}, kitchen={rms.kitchen}, dining={rms.dining},
  garage={rms.garage}, study={rms.study}
- Style: {request.preferred_style}
- Budget: {request.budget}
- Region: {request.region}
- Notes: {request.description or 'None'}
"""
    if site:
        ctx += f"\n## Site Analysis\n{site.raw or ''}\n"
    if style_ref:
        ctx += f"\n## Style Reference\nColors: {style_ref.colors}\nFeatures: {style_ref.features}\n"
    if validation_errors:
        ctx += f"\n## ⚠️ Fix These Geometry Errors\n"
        for e in validation_errors:
            ctx += f"- {e}\n"

    ctx += f"""
## Instructions
- ALL rooms must fit within {plot.length}m × {plot.width}m per floor
- Rooms must NOT overlap
- Each room MUST have: name, width, depth, x, y, floor, has_window, has_door, door_wall
- Use metric units (meters)
- Respond ONLY with a single JSON object matching this schema exactly:
{_SCHEMA_HINT}
"""
    return ctx


# ─────────────────────────── JSON Extraction ────────────────────────────────

def _extract_json(text: str) -> Optional[dict]:
    """Extract first valid JSON object from text."""
    # Try code block first
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass

    # Find outermost { ... }
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


# ─────────────────────────── Spec Adaptation ────────────────────────────────

def _adapt_spec(raw: dict) -> dict:
    """Normalise Gemini output to match BuildingSpec schema."""
    # Ensure floors list
    if "floors" not in raw or not isinstance(raw["floors"], list):
        raw["floors"] = []

    for fl in raw["floors"]:
        if "rooms" not in fl:
            fl["rooms"] = []
        for rm in fl.get("rooms", []):
            # rename label → name if needed
            if "label" in rm and "name" not in rm:
                rm["name"] = rm.pop("label")
            if "name" not in rm:
                rm["name"] = "Room"
            # ensure floor field
            if "floor" not in rm:
                rm["floor"] = fl.get("floor_number", 0)
            # ensure door_wall
            if "door_wall" not in rm:
                rm["door_wall"] = "south"

    # Camera aliases
    cam = raw.get("camera", {})
    if "location" in cam and "pos" not in cam:
        cam["pos"] = cam.pop("location")
    if "target" in cam and "look_at" not in cam:
        cam["look_at"] = cam.pop("target")
    raw["camera"] = cam

    return raw


# ─────────────────────────── Main Agent ──────────────────────────────────────

class ArchitectAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY", "")
        self._client = genai.Client(api_key=api_key)

    def generate(
        self,
        request: GenerateRequest,
        site: Optional[SiteAnalysis] = None,
        style_ref: Optional[StyleAnalysis] = None,
        validation_errors: Optional[list[str]] = None,
        max_retries: int = 2,
    ) -> BuildingSpec:
        prompt = _build_prompt(request, site, style_ref, validation_errors)

        for attempt in range(max_retries + 1):
            try:
                response = self._client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                )
                text = response.text or ""
                raw = _extract_json(text)
                if raw is None:
                    logger.warning("Attempt %d: no JSON found in Gemini response", attempt)
                    continue
                raw = _adapt_spec(raw)
                spec = BuildingSpec.model_validate(raw)
                logger.info("BuildingSpec generated successfully on attempt %d", attempt)
                return spec
            except Exception as exc:
                logger.error("Attempt %d failed: %s", attempt, exc)

        logger.warning("All Gemini attempts failed — using DEFAULT_SPEC")
        return DEFAULT_SPEC
