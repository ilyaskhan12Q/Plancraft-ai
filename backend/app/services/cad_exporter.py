"""
NanoCAD-compatible CAD exporter using ezdxf.
Handles layers, line types, and blocks for professional floor plans.
"""
from __future__ import annotations
import os
from pathlib import Path
from typing import List

import ezdxf
from ezdxf.enums import TextEntityAlignment

from app.models.schemas import BuildingSpec, RoomSpec, FloorSpec

# ── CAD Constants ────────────────────────────────────────────────────────────
LAYER_WALLS = "A-WALL"
LAYER_ROOMS = "A-ROOM"
LAYER_DOORS = "A-DOOR"
LAYER_WINDOW = "A-GLAZ"
LAYER_TEXT = "A-TEXT"
LAYER_DIM = "A-DIM"

COLOR_WALL_OUTER = 7  # White/Black
COLOR_WALL_INNER = 8  # Dark Grey
COLOR_DOOR = 1        # Red
COLOR_WINDOW = 4      # Cyan
COLOR_TEXT = 252      # Light Grey
COLOR_DIM = 251       # Grey


def export_to_dxf(spec: BuildingSpec, output_dir: str) -> str:
    """
    Export BuildingSpec to a professional DXF file.
    Returns the absolute path to the saved DXF.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    out_path = os.path.join(output_dir, "floor_plan.dxf")

    doc = ezdxf.new("R2010")  # Compatibility for most CAD versions including nanoCAD
    msp = doc.modelspace()

    # Create Layers
    doc.layers.add(LAYER_WALLS, color=COLOR_WALL_OUTER)
    doc.layers.add(LAYER_ROOMS, color=COLOR_TEXT)
    doc.layers.add(LAYER_DOORS, color=COLOR_DOOR)
    doc.layers.add(LAYER_WINDOW, color=COLOR_WINDOW)
    doc.layers.add(LAYER_TEXT, color=COLOR_TEXT)
    doc.layers.add(LAYER_DIM, color=COLOR_DIM)

    # Offset for multi-floor side-by-side display
    offset_x = 0
    gap = 5.0

    for fl in sorted(spec.floors, key=lambda f: f.floor_number):
        if not fl.rooms:
            continue

        min_rm_x = min(rm.x for rm in fl.rooms)
        floor_w = max(rm.x + rm.width for rm in fl.rooms) - min_rm_x

        _draw_floor_dxf(msp, fl, floor_offset_x = offset_x - min_rm_x)
        
        # Add Floor Label
        label = f"FLOOR {fl.floor_number}" if fl.floor_number > 0 else "GROUND FLOOR"
        msp.add_text(
            label,
            dxfattribs={"layer": LAYER_TEXT, "height": 0.5, "style": "Standard"}
        ).set_placement((offset_x + floor_w / 2, -1.5), align=TextEntityAlignment.CENTER)

        offset_x += floor_w + gap

    doc.saveas(out_path)
    return out_path


def _draw_floor_dxf(msp, floor: FloorSpec, floor_offset_x: float) -> None:
    """Draw rooms, doors, and windows for a single floor."""
    for rm in floor.rooms:
        x1 = rm.x + floor_offset_x
        y1 = rm.y
        x2 = x1 + rm.width
        y2 = y1 + rm.depth

        # Draw outer walls (thick line effect via polyline)
        points = [(x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)]
        msp.add_lwpolyline(points, dxfattribs={"layer": LAYER_WALLS, "const_width": 0.05})

        # Room Label
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        msp.add_text(
            rm.name.upper(),
            dxfattribs={"layer": LAYER_TEXT, "height": 0.3}
        ).set_placement((cx, cy + 0.2), align=TextEntityAlignment.CENTER)
        
        area_label = f"{rm.width * rm.depth:.1f} m2"
        msp.add_text(
            area_label,
            dxfattribs={"layer": LAYER_TEXT, "height": 0.2}
        ).set_placement((cx, cy - 0.2), align=TextEntityAlignment.CENTER)

        # Doors
        if rm.has_door:
            _draw_door_dxf(msp, rm, floor_offset_x)

        # Windows
        if rm.has_window:
            _draw_window_dxf(msp, rm, floor_offset_x)


def _draw_door_dxf(msp, rm: RoomSpec, offset_x: float) -> None:
    """Draw a basic door symbol in DXF."""
    x = rm.x + offset_x
    y = rm.y
    w = rm.width
    d = rm.depth
    dw = min(w, d) * 0.2
    wall = rm.door_wall

    if wall == "south":
        p1 = (x + w/2 - dw/2, y)
        p2 = (x + w/2 + dw/2, y)
        msp.add_line(p1, p2, dxfattribs={"layer": LAYER_DOORS, "color": 1}) # Red for door
    elif wall == "north":
        p1 = (x + w/2 - dw/2, y + d)
        p2 = (x + w/2 + dw/2, y + d)
        msp.add_line(p1, p2, dxfattribs={"layer": LAYER_DOORS, "color": 1})
    elif wall == "east":
        p1 = (x + w, y + d/2 - dw/2)
        p2 = (x + w, y + d/2 + dw/2)
        msp.add_line(p1, p2, dxfattribs={"layer": LAYER_DOORS, "color": 1})
    else: # west
        p1 = (x, y + d/2 - dw/2)
        p2 = (x, y + d/2 + dw/2)
        msp.add_line(p1, p2, dxfattribs={"layer": LAYER_DOORS, "color": 1})


def _draw_window_dxf(msp, rm: RoomSpec, offset_x: float) -> None:
    """Draw a window symbol in DXF (double line)."""
    x = rm.x + offset_x
    y = rm.y
    w = rm.width
    d = rm.depth
    ww = w * 0.4
    wx = x + (w - ww) / 2
    wy = y + d

    # Window lines
    msp.add_line((wx, wy + 0.05), (wx + ww, wy + 0.05), dxfattribs={"layer": LAYER_WINDOW})
    msp.add_line((wx, wy - 0.05), (wx + ww, wy - 0.05), dxfattribs={"layer": LAYER_WINDOW})
