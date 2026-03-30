"""
Design Critique Agent.
After generating a BuildingSpec, asks Gemini to review its own output
as a senior architect and return 3–5 actionable critique notes.
"""
from __future__ import annotations
import logging
import os
from typing import Optional

from dotenv import load_dotenv
from google import genai

from app.models.schemas import BuildingSpec, GenerateRequest

load_dotenv()
logger = logging.getLogger(__name__)


def _build_critique_prompt(spec: BuildingSpec, request: GenerateRequest) -> str:
    # Build a human-readable summary of the design
    room_summary = []
    for fl in spec.floors:
        for rm in fl.rooms:
            room_summary.append(
                f"  Floor {fl.floor_number}: {rm.name} ({rm.width}m × {rm.depth}m)"
            )

    rooms_text = "\n".join(room_summary)

    return f"""You are a senior licensed architect reviewing a residential building design.

## Design Details
- Plot: {request.plot.length}m × {request.plot.width}m, {request.plot.floors} floor(s)
- Road facing: {request.plot.orientation}
- Budget: {request.budget}, Region: {request.region}
- Style: {request.preferred_style}
- Rooms in the design:
{rooms_text}

## Your Task
Review this layout critically as an experienced architect. Give exactly 3 to 5 concise critique points covering:
- What works well in this design ✅
- What could be improved or is a risk ⚠️
- One practical engineering suggestion 🔧

Respond ONLY as a JSON array of strings. Each item is one bullet point (1–2 sentences max). Example:
["✅ The open-plan living and dining creates excellent visual flow.", "⚠️ Bathroom on floor 1 has no external wall — natural ventilation will require a mechanical fan.", "🔧 Consider shifting the staircase to the centre to reduce corridor length by ~2m."]
"""


class CritiqueAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY", "")
        self._client = genai.Client(api_key=api_key)

    def critique(
        self,
        spec: BuildingSpec,
        request: GenerateRequest,
    ) -> list[str]:
        """
        Returns a list of critique bullet-point strings.
        Falls back to an empty list on any error.
        """
        prompt = _build_critique_prompt(spec, request)
        try:
            response = self._client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            text = (response.text or "").strip()
            # Extract JSON array
            import json, re
            m = re.search(r"\[.*\]", text, re.DOTALL)
            if m:
                items = json.loads(m.group(0))
                if isinstance(items, list):
                    logger.info("Design critique generated: %d points", len(items))
                    return [str(i) for i in items[:5]]
        except Exception as exc:
            logger.warning("Critique agent failed: %s", exc)
        return []
