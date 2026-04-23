"""
Critique Agent — provides expert architectural design feedback using Gemini.
Evaluates spatial flow, biophilic design, wellness architecture,
indoor-outdoor connectivity, and engineering standards.
"""
from __future__ import annotations
import json
import logging
import os
import re
from typing import List, Optional

from dotenv import load_dotenv
from google import genai

from app.models.schemas import BuildingSpec, CritiquePoint, DesignCritique

load_dotenv()
logger = logging.getLogger(__name__)


def _extract_json(text: str) -> Optional[dict]:
    """Extract first valid JSON object from text."""
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
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


class CritiqueAgent:
    """Generates expert architectural critique for a completed building design."""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY", "")
        self._client = genai.Client(api_key=api_key)

    def critique(self, spec: BuildingSpec) -> DesignCritique:
        """Evaluate the design and return structured critique."""
        # Build room summary
        room_summary = []
        for fl in spec.floors:
            for rm in fl.rooms:
                room_summary.append(
                    f"  - Floor {fl.floor_number}: {rm.name} "
                    f"({rm.width}m × {rm.depth}m at ({rm.x},{rm.y}), "
                    f"window={rm.has_window}, door={rm.has_door}/{rm.door_wall})"
                )
        rooms_text = "\n".join(room_summary)

        total_area = sum(rm.width * rm.depth for fl in spec.floors for rm in fl.rooms)

        prompt = f"""You are a senior architectural critic and design reviewer with 25+ years of experience.
Evaluate the following building design and provide a detailed, constructive critique.

## Building Design
- Style: {spec.style}
- Floors: {len(spec.floors)}
- Exterior: {spec.facade_material}, Color: {spec.exterior_color}
- Roof: {spec.roof_type}, Color: {spec.roof_color}
- Windows: {spec.window_type}
- Total built area: {total_area:.1f} m²

## Room Layout
{rooms_text}

## Evaluation Criteria
Rate each category from 1-10 and provide specific feedback:

1. **Spatial Flow** — How well do rooms connect? Is circulation efficient?
2. **Natural Light** — Window placement, room orientation for daylight
3. **Ventilation** — Cross-ventilation potential, air circulation paths
4. **Privacy** — Separation between public/private zones
5. **Biophilic Design** — Connection to nature, green spaces, natural materials
6. **Structural Efficiency** — Load-bearing wall alignment, structural grid
7. **Accessibility** — Ease of movement, doorway widths, bathroom access
8. **Overall Design Quality** — Aesthetic coherence, proportions, style consistency

## Response Format
Return ONLY a JSON object:
{{
  "overall_score": 7.5,
  "overall_verdict": "A solid design with good spatial flow but room for improvement in natural light access",
  "points": [
    {{
      "category": "Spatial Flow",
      "score": 8,
      "feedback": "Detailed feedback here",
      "suggestion": "Specific improvement suggestion"
    }}
  ],
  "strengths": ["strength1", "strength2"],
  "weaknesses": ["weakness1", "weakness2"],
  "top_recommendations": ["recommendation1", "recommendation2", "recommendation3"]
}}
"""
        try:
            response = self._client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            text = response.text or ""
            raw = _extract_json(text)

            if raw is None:
                logger.warning("No JSON found in critique response")
                return DesignCritique(
                    overall_score=0,
                    overall_verdict="Critique unavailable",
                    points=[], strengths=[], weaknesses=[],
                    top_recommendations=[],
                    raw_response=text,
                )

            points = []
            for p in raw.get("points", []):
                try:
                    points.append(CritiquePoint(
                        category=p.get("category", "General"),
                        score=p.get("score", 5),
                        feedback=p.get("feedback", ""),
                        suggestion=p.get("suggestion", ""),
                    ))
                except Exception as e:
                    logger.warning("Skipping invalid critique point: %s", e)

            critique = DesignCritique(
                overall_score=raw.get("overall_score", 0),
                overall_verdict=raw.get("overall_verdict", ""),
                points=points,
                strengths=raw.get("strengths", []),
                weaknesses=raw.get("weaknesses", []),
                top_recommendations=raw.get("top_recommendations", []),
                raw_response=text,
            )
            logger.info("Design critique generated: score=%.1f", critique.overall_score)
            return critique

        except Exception as exc:
            logger.error("Design critique failed: %s", exc)
            return DesignCritique(
                overall_score=0,
                overall_verdict=f"Critique error: {exc}",
                points=[], strengths=[], weaknesses=[],
                top_recommendations=[],
                raw_response=str(exc),
            )
