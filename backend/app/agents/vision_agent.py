"""
Vision agent — uses Gemini Vision to analyse uploaded site/style/sketch photos.
"""
from __future__ import annotations
import base64
import json
import logging
import os
import re
from pathlib import Path
from typing import Optional, Tuple

from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.models.schemas import SiteAnalysis, StyleAnalysis

load_dotenv()
logger = logging.getLogger(__name__)


def _encode_image(path: str) -> Tuple[str, str]:
    """Return (base64_data, mime_type) for an image file."""
    p = Path(path)
    suffix = p.suffix.lower()
    mime = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }.get(suffix, "image/jpeg")
    data = base64.standard_b64encode(p.read_bytes()).decode()
    return data, mime


def _extract_json(text: str) -> Optional[dict]:
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


class VisionAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY", "")
        self._client = genai.Client(api_key=api_key)

    def analyse_site(self, image_path: str) -> SiteAnalysis:
        """Analyse a site photo and return structured site info."""
        try:
            data, mime = _encode_image(image_path)
            prompt = """Analyse this site photo for architectural purposes.
Return ONLY a JSON object:
{
  "terrain": "flat|sloped|rocky|...",
  "vegetation": "none|trees|bushes|...",
  "road_facing": "north|south|east|west|unknown",
  "constraints": "brief description of any constraints visible"
}"""
            response = self._client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_bytes(data=base64.b64decode(data), mime_type=mime),
                            types.Part.from_text(text=prompt),
                        ],
                    )
                ],
            )
            raw = _extract_json(response.text or "")
            if raw:
                return SiteAnalysis(raw=response.text, **{k: v for k, v in raw.items()
                                                          if k in SiteAnalysis.model_fields})
        except Exception as exc:
            logger.error("Site vision analysis failed: %s", exc)
        return SiteAnalysis(raw="Analysis unavailable")

    def analyse_style(self, image_path: str) -> StyleAnalysis:
        """Analyse a style reference photo."""
        try:
            data, mime = _encode_image(image_path)
            prompt = """Analyse this architectural style reference photo.
Return ONLY a JSON object:
{
  "detected_style": "modern|traditional|minimalist|...",
  "colors": ["#hex1", "#hex2"],
  "features": ["flat roof", "large windows", "open plan", ...]
}"""
            response = self._client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_bytes(data=base64.b64decode(data), mime_type=mime),
                            types.Part.from_text(text=prompt),
                        ],
                    )
                ],
            )
            raw = _extract_json(response.text or "")
            if raw:
                return StyleAnalysis(raw=response.text, **{k: v for k, v in raw.items()
                                                           if k in StyleAnalysis.model_fields})
        except Exception as exc:
            logger.error("Style vision analysis failed: %s", exc)
        return StyleAnalysis(raw="Analysis unavailable")
