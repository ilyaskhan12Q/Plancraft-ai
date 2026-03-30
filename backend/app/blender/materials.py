"""
PBR material library for Blender script generation.
Each entry contains Blender Principled BSDF parameters.
"""
from __future__ import annotations
from typing import Dict, Any

# Material name → Principled BSDF parameters
MATERIALS: Dict[str, Dict[str, Any]] = {
    # ── Exterior walls ────────────────────────────────────────────
    "plaster": {
        "base_color": (0.96, 0.96, 0.94, 1.0),
        "roughness": 0.85,
        "metallic": 0.0,
        "specular": 0.1,
    },
    "brick": {
        "base_color": (0.72, 0.38, 0.25, 1.0),
        "roughness": 0.90,
        "metallic": 0.0,
        "specular": 0.05,
    },
    "concrete": {
        "base_color": (0.55, 0.55, 0.55, 1.0),
        "roughness": 0.80,
        "metallic": 0.0,
        "specular": 0.05,
    },
    "wood": {
        "base_color": (0.62, 0.42, 0.22, 1.0),
        "roughness": 0.70,
        "metallic": 0.0,
        "specular": 0.1,
    },
    "stone": {
        "base_color": (0.60, 0.55, 0.50, 1.0),
        "roughness": 0.88,
        "metallic": 0.0,
        "specular": 0.05,
    },
    "marble": {
        "base_color": (0.92, 0.90, 0.88, 1.0),
        "roughness": 0.15,
        "metallic": 0.0,
        "specular": 0.8,
    },
    # ── Roof ──────────────────────────────────────────────────────
    "roof_flat": {
        "base_color": (0.30, 0.30, 0.30, 1.0),
        "roughness": 0.90,
        "metallic": 0.0,
        "specular": 0.02,
    },
    "roof_tile": {
        "base_color": (0.65, 0.28, 0.15, 1.0),
        "roughness": 0.85,
        "metallic": 0.0,
        "specular": 0.05,
    },
    "roof_metal": {
        "base_color": (0.45, 0.50, 0.55, 1.0),
        "roughness": 0.30,
        "metallic": 0.9,
        "specular": 0.6,
    },
    # ── Glass / Windows ───────────────────────────────────────────
    "glass": {
        "base_color": (0.70, 0.85, 0.95, 0.1),
        "roughness": 0.0,
        "metallic": 0.0,
        "specular": 1.0,
        "transmission": 0.95,
        "ior": 1.45,
    },
    # ── Doors ─────────────────────────────────────────────────────
    "door_wood": {
        "base_color": (0.40, 0.25, 0.10, 1.0),
        "roughness": 0.60,
        "metallic": 0.0,
        "specular": 0.15,
    },
    "door_metal": {
        "base_color": (0.20, 0.20, 0.25, 1.0),
        "roughness": 0.25,
        "metallic": 0.9,
        "specular": 0.7,
    },
    # ── Ground ────────────────────────────────────────────────────
    "grass": {
        "base_color": (0.18, 0.38, 0.12, 1.0),
        "roughness": 0.95,
        "metallic": 0.0,
        "specular": 0.0,
    },
    "pavement": {
        "base_color": (0.50, 0.50, 0.48, 1.0),
        "roughness": 0.90,
        "metallic": 0.0,
        "specular": 0.02,
    },
}


def get_material(name: str) -> Dict[str, Any]:
    """Return material params, falling back to plaster if unknown."""
    return MATERIALS.get(name, MATERIALS["plaster"])


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert '#RRGGBB' to linear (r, g, b, 1.0) tuple."""
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return (0.9, 0.9, 0.9, 1.0)
    r, g, b = (int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    # Approximate sRGB → linear
    def lin(c): return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (lin(r), lin(g), lin(b), 1.0)
