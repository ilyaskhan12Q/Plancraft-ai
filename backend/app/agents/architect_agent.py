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

# ─────────────────────────── Style Archetypes ────────────────────────────────

_STYLE_ARCHETYPES = {
    "low": (
        "Pakistani Cost-Saver",
        "Use load-bearing brick construction. Minimise corridors — open layout. "
        "Standard 9×4.5 inch brick walls. Flat reinforced-concrete roof. "
        "Prefer shared bathroom walls to reduce plumbing runs. "
        "Target cost: PKR 3,000–3,800/sqft."
    ),
    "medium": (
        "Contemporary South Asian",
        "Use RCC frame with brick infill. Include a proper entrance hall/lobby. "
        "Balcony on upper floor(s). Tiled exterior finish. "
        "Target cost: PKR 4,000–5,500/sqft."
    ),
    "high": (
        "Modern Minimalist",
        "RCC frame, open-plan living/dining, floor-to-ceiling glazing on south/garden side. "
        "Imported marble flooring. Concealed wiring and plumbing. "
        "Feature staircase as design element. Target cost: PKR 6,000–8,000/sqft."
    ),
    "luxury": (
        "Luxury Contemporary",
        "Double-height entrance lobby, home theatre, en-suite for every bedroom. "
        "Smart-home wiring. Rooftop terrace. Imported stone cladding. "
        "Target cost: PKR 9,000+/sqft."
    ),
}

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
                         floor=0, has_window=True, has_door=False, door_wall="none"),
                RoomSpec(name="Dining",      width=3.0, depth=3.0, x=5.0, y=3.0,
                         floor=0, has_window=True, has_door=False, door_wall="none"),
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
        },
        {
          "name": "Open Kitchen",
          "width": 3.0,
          "depth": 3.0,
          "x": 5.0,
          "y": 0.0,
          "floor": 0,
          "has_window": true,
          "has_door": false,
          "door_wall": "none"
        }
      ]
    }
  ]
}
"""

# ─────────────────────────── Engineering Rules ───────────────────────────────

_ENGINEERING_RULES = """\
## Engineering & Building Standards
You MUST follow these professional standards:

### Room Sizes (minimum)
- Bedroom: 9m² minimum (e.g. 3m × 3m)
- Master Bedroom: 12m² minimum (e.g. 3.5m × 3.5m)
- Bathroom: 4m² minimum (e.g. 2m × 2m)
- Kitchen: 6m² minimum (e.g. 2.5m × 2.4m)
- Living Room: 15m² minimum (e.g. 4m × 4m)
- Corridor / Hall: 1.5m wide minimum

### Circulation
- Ground floor MUST have an entrance hall or lobby connecting to other rooms
- Upper floors MUST have a landing area connecting to bedrooms
- Every floor with bedrooms must have at least one bathroom on the same floor

### Window & Door Placement
- Bedrooms MUST have has_window=true (natural light requirement)
- Bathrooms facing road should use frosted windows (set has_window=false if no privacy possible)
- Open-plan rooms (Kitchen open to Living, etc.) must use door_wall="none" and has_door=false
- Main entrance door MUST face either the road-facing direction or within 90° of it

### Structural
- Do NOT place rooms with overlapping coordinates
- ALL rooms must fit within the plot bounds (0,0) to (plot_length, plot_width)
- Floor height must be between 2.8m and 4.0m

### door_wall RULES (CRITICAL)
- ONLY allowed values: "north", "south", "east", "west", "none"
- Use "none" ONLY for open-plan spaces (kitchen open to dining, etc.)
- NEVER use "none" for bedrooms or bathrooms — they MUST have a real door_wall
- NEVER leave door_wall blank or set it to null
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

    # Pick style archetype
    budget_key = request.budget if request.budget in _STYLE_ARCHETYPES else "medium"
    archetype_name, archetype_guide = _STYLE_ARCHETYPES[budget_key]

<<<<<<< HEAD
    ctx = f"""You are a world-class Lead Architect specializing in {request.region} residential design.
=======
    ctx = f"""You are a senior licensed architect with 20 years of experience in {request.region} residential design.
Your designs are functional, structurally sound, and optimised for the client's budget.
>>>>>>> parent of a8c1d73 (Enhance 2D design with multi-floor support, detailed plot inputs, and 2026 architectural reasoning)

## Style Persona: {archetype_name}
{archetype_guide}

## Project Brief
<<<<<<< HEAD
- Plot Size: {plot.length}m × {plot.width}m ({marla_hint})
- Plot Type: {plot.plot_type}, Road-facing: {plot.orientation}
- Setbacks: Front={plot.setbacks.front}m, Back={plot.setbacks.back}m, Sides={plot.setbacks.left}m/{plot.setbacks.right}m
- Floors: {plot.floors}
- Rooms requested: {rms.bedrooms} bedrooms, {rms.bathrooms} bathrooms, living={rms.living_room}, kitchen={rms.kitchen}, dining={rms.dining}, garage={rms.garage}, study={rms.study}

## Engineering & Pakistani Architectural Standards (MANDATORY)
1. **The Drawing Room (Guest Room)**: MUST be near the main entrance with a separate door for guests.
2. **TV Lounge**: Central circulation hub for the family.
3. **Attached Bathrooms**: EVERY bedroom MUST have an attached bathroom.
4. **Layout**: Use a logical, leak-proof grid. NO OVERLAPPING ROOMS.

## Task: Generate COMPLETE Building Specification
- Create a distinct and logical layout for EVERY floor.
- Respond ONLY with a single valid JSON object following this schema:
{_SCHEMA_HINT}
=======
- Plot: {plot.length}m × {plot.width}m ({plot.length * plot.width:.0f}m² = {plot.length * plot.width * 10.764:.0f} sqft)
- Floors: {plot.floors}, Road-facing: {plot.orientation}
- Rooms requested: {rms.bedrooms} bedrooms, {rms.bathrooms} bathrooms,
  living={rms.living_room}, kitchen={rms.kitchen}, dining={rms.dining},
  garage={rms.garage}, study={rms.study}, servant_quarter={rms.servant_quarter}
- Preferred style: {request.preferred_style}
- Budget tier: {request.budget}
- Region: {request.region}
- Client notes: {request.description or 'None'}
>>>>>>> parent of a8c1d73 (Enhance 2D design with multi-floor support, detailed plot inputs, and 2026 architectural reasoning)
"""
    if site:
        ctx += f"\n## Site Analysis\n{site.raw or ''}\n"
    if style_ref:
        ctx += f"\n## Style Reference\nColors: {style_ref.colors}\nFeatures: {style_ref.features}\n"
    if validation_errors:
        ctx += f"\n## ⚠️ GEOMETRY ERRORS — YOU MUST FIX THESE\n"
        for e in validation_errors:
            ctx += f"- {e}\n"
        ctx += "\nRe-generate the COMPLETE building spec with these errors corrected.\n"

    ctx += f"""
{_ENGINEERING_RULES}

## Response Format
- Respond ONLY with a single valid JSON object — no explanation, no markdown prose
- Match this schema exactly (door_wall can be "north"/"south"/"east"/"west"/"none"):
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
    if "floors" not in raw or not isinstance(raw["floors"], list):
        raw["floors"] = []

    VALID_DOOR_WALLS = {"north", "south", "east", "west", "none"}

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
            # fix door_wall — map invalid values to a sensible default
            dw = str(rm.get("door_wall", "")).strip().lower()
            if dw not in VALID_DOOR_WALLS:
                # rooms with no door → "none", rooms with a door → "south"
                rm["door_wall"] = "none" if not rm.get("has_door", True) else "south"
            else:
                rm["door_wall"] = dw

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
                    model="gemini-flash-lite-latest",
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
