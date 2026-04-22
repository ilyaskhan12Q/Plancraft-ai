"""
2D floor plan renderer using matplotlib.
Produces professional architectural-grade floor plans with:
- Multi-floor rendering (all floors side-by-side)
- Dimension lines with arrows
- Room area labels
- Proper wall thickness
- Grid overlay
- North arrow and scale bar
- Door arcs and window marks
"""
from __future__ import annotations
import math
import os
from pathlib import Path
from typing import List, Tuple

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, FancyArrowPatch
import matplotlib.patheffects as pe
import numpy as np

from app.models.schemas import BuildingSpec, RoomSpec, FloorSpec


# ── Color palette ──────────────────────────────────────────────────────────
ROOM_COLORS = {
    "default": "#F5F5F0",
    "bedroom": "#E8EDF5",
    "bathroom": "#D6EAF8",
    "kitchen": "#FDF2E9",
    "living": "#E8F8F5",
    "dining": "#FDEBD0",
    "hallway": "#F2F3F4",
    "stairwell": "#FADBD8",
    "foyer": "#FCF3CF",
    "entry": "#FCF3CF",
    "garage": "#E5E8E8",
    "study": "#E8DAEF",
    "master": "#D5F5E3",
    "servant": "#F2F3F4",
}

WALL_COLOR = "#1A1A2E"
WALL_INNER = "#2C3E50"
DOOR_COLOR = "#8B4513"
WINDOW_COLOR = "#2E86C1"
TEXT_COLOR = "#0D0D0D"
DIM_COLOR = "#555555"
GRID_COLOR = "#E0E0E0"
AREA_COLOR = "#7F8C8D"
TITLE_COLOR = "#1A1A2E"
HATCH_COLOR = "#B0C4DE"


def _get_room_color(name: str) -> str:
    """Pick room color based on name keywords."""
    lower = name.lower()
    for key, color in ROOM_COLORS.items():
        if key in lower:
            return color
    return ROOM_COLORS["default"]


def _draw_room(ax, rm: RoomSpec, floor_offset_x: float = 0) -> None:
    """Draw a single room with double-line walls, labels, and area."""
    x = rm.x + floor_offset_x
    y = rm.y
    w = rm.width
    d = rm.depth
    color = _get_room_color(rm.name)

    # Room fill
    rect = patches.Rectangle(
        (x, y), w, d,
        linewidth=0, edgecolor="none",
        facecolor=color, zorder=2,
    )
    ax.add_patch(rect)

    # Outer walls (thick)
    wall_rect = patches.Rectangle(
        (x, y), w, d,
        linewidth=2.5, edgecolor=WALL_COLOR,
        facecolor="none", zorder=4,
    )
    ax.add_patch(wall_rect)

    # Inner wall line (thin for double-wall effect)
    inset = 0.08
    inner_rect = patches.Rectangle(
        (x + inset, y + inset), w - 2 * inset, d - 2 * inset,
        linewidth=0.8, edgecolor=WALL_INNER,
        facecolor="none", zorder=4, linestyle="-",
    )
    ax.add_patch(inner_rect)

    # Hatching for bathrooms
    if "bathroom" in rm.name.lower() or "bath" in rm.name.lower():
        hatch_rect = patches.Rectangle(
            (x, y), w, d,
            linewidth=0, facecolor="none",
            hatch="///", edgecolor=HATCH_COLOR, zorder=3, alpha=0.3,
        )
        ax.add_patch(hatch_rect)

    # Room label (centered)
    cx, cy = x + w / 2, y + d / 2
    ax.text(
        cx, cy + d * 0.08, rm.name,
        ha="center", va="center",
        fontsize=7.5, fontweight="bold", color=TEXT_COLOR,
        zorder=6,
        path_effects=[pe.withStroke(linewidth=2, foreground="white")],
    )

    # Area label
    area = w * d
    ax.text(
        cx, cy - d * 0.12,
        f"{area:.1f} m²",
        ha="center", va="center",
        fontsize=6, color=AREA_COLOR, fontstyle="italic",
        zorder=6,
        path_effects=[pe.withStroke(linewidth=2, foreground="white")],
    )

    # Door arc
    if rm.has_door:
        _draw_door(ax, rm, floor_offset_x)

    # Window marks
    if rm.has_window:
        _draw_window(ax, rm, floor_offset_x)


def _draw_door(ax, rm: RoomSpec, offset_x: float = 0) -> None:
    """Draw door arc on the specified wall."""
    x = rm.x + offset_x
    y = rm.y
    w = rm.width
    d = rm.depth
    dw = min(w, d) * 0.25
    wall = rm.door_wall

    if wall == "south":
        ox, oy = x + w / 2 - dw / 2, y
        arc = Arc((ox, oy), dw * 2, dw * 2, angle=0, theta1=0, theta2=90,
                  color=DOOR_COLOR, linewidth=1.0, zorder=5)
        ax.add_patch(arc)
        ax.plot([ox, ox + dw], [oy, oy], color=DOOR_COLOR, lw=1.0, zorder=5)
    elif wall == "north":
        ox, oy = x + w / 2 - dw / 2, y + d
        arc = Arc((ox, oy), dw * 2, dw * 2, angle=0, theta1=270, theta2=360,
                  color=DOOR_COLOR, linewidth=1.0, zorder=5)
        ax.add_patch(arc)
        ax.plot([ox, ox + dw], [oy, oy], color=DOOR_COLOR, lw=1.0, zorder=5)
    elif wall == "east":
        ox, oy = x + w, y + d / 2 - dw / 2
        arc = Arc((ox, oy), dw * 2, dw * 2, angle=90, theta1=0, theta2=90,
                  color=DOOR_COLOR, linewidth=1.0, zorder=5)
        ax.add_patch(arc)
        ax.plot([ox, ox], [oy, oy + dw], color=DOOR_COLOR, lw=1.0, zorder=5)
    else:  # west
        ox, oy = x, y + d / 2 - dw / 2
        arc = Arc((ox, oy), dw * 2, dw * 2, angle=90, theta1=270, theta2=360,
                  color=DOOR_COLOR, linewidth=1.0, zorder=5)
        ax.add_patch(arc)
        ax.plot([ox, ox], [oy, oy + dw], color=DOOR_COLOR, lw=1.0, zorder=5)


def _draw_window(ax, rm: RoomSpec, offset_x: float = 0) -> None:
    """Draw a double-line window mark on the north wall with gaps."""
    x = rm.x + offset_x
    y = rm.y
    w = rm.width
    d = rm.depth
    ww = w * 0.35
    wx = x + (w - ww) / 2
    wy = y + d

    # Three-line window symbol (architectural standard)
    for offset in [-0.06, 0.0, 0.06]:
        ax.plot(
            [wx, wx + ww], [wy + offset, wy + offset],
            color=WINDOW_COLOR, lw=1.2, zorder=5,
        )
    # Gap markers at ends
    for ex in [wx, wx + ww]:
        ax.plot(
            [ex, ex], [wy - 0.08, wy + 0.08],
            color=WINDOW_COLOR, lw=1.5, zorder=5,
        )


def _draw_dimension(ax, x1: float, y1: float, x2: float, y2: float,
                     offset: float = -0.5, label: str = "") -> None:
    """Draw a dimension line with arrows and a measurement label."""
    # Extension lines
    if abs(y1 - y2) < 0.01:  # horizontal
        ax.plot([x1, x1], [y1, y1 + offset], color=DIM_COLOR, lw=0.5, zorder=1)
        ax.plot([x2, x2], [y2, y2 + offset], color=DIM_COLOR, lw=0.5, zorder=1)
        mid_x = (x1 + x2) / 2
        mid_y = y1 + offset
        ax.annotate(
            "", xy=(x2, mid_y), xytext=(x1, mid_y),
            arrowprops=dict(arrowstyle="<->", color=DIM_COLOR, lw=0.8),
            zorder=1,
        )
        dist = abs(x2 - x1)
        lbl = label or f"{dist:.1f}m"
        ax.text(mid_x, mid_y - 0.15, lbl, ha="center", va="top",
                fontsize=5.5, color=DIM_COLOR, zorder=1,
                bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.8))
    else:  # vertical
        ax.plot([x1, x1 + offset], [y1, y1], color=DIM_COLOR, lw=0.5, zorder=1)
        ax.plot([x2, x2 + offset], [y2, y2], color=DIM_COLOR, lw=0.5, zorder=1)
        mid_x = x1 + offset
        mid_y = (y1 + y2) / 2
        ax.annotate(
            "", xy=(mid_x, y2), xytext=(mid_x, y1),
            arrowprops=dict(arrowstyle="<->", color=DIM_COLOR, lw=0.8),
            zorder=1,
        )
        dist = abs(y2 - y1)
        lbl = label or f"{dist:.1f}m"
        ax.text(mid_x - 0.15, mid_y, lbl, ha="right", va="center",
                fontsize=5.5, color=DIM_COLOR, rotation=90, zorder=1,
                bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.8))


def _draw_grid(ax, min_x: float, max_x: float, min_y: float, max_y: float) -> None:
    """Draw a light grid overlay for scale reference."""
    for x in range(int(min_x), int(max_x) + 1):
        ax.axvline(x, color=GRID_COLOR, linewidth=0.3, zorder=0)
    for y in range(int(min_y), int(max_y) + 1):
        ax.axhline(y, color=GRID_COLOR, linewidth=0.3, zorder=0)


def _draw_north_arrow(ax, x: float, y: float, length: float = 0.8) -> None:
    ax.annotate(
        "", xy=(x, y + length), xytext=(x, y),
        arrowprops=dict(arrowstyle="-|>", color="black", lw=1.8),
        zorder=7,
    )
    ax.text(x, y + length + 0.15, "N", ha="center", va="bottom",
            fontsize=9, fontweight="bold", color="black", zorder=7)


def _draw_scale_bar(ax, x: float, y: float, scale_m: float = 5.0) -> None:
    ax.annotate(
        "", xy=(x + scale_m, y), xytext=(x, y),
        arrowprops=dict(arrowstyle="|-|", color="black", lw=1.5),
        zorder=7,
    )
    ax.text(x + scale_m / 2, y - 0.3, f"{scale_m:.0f}m",
            ha="center", va="top", fontsize=7, color="black", zorder=7)


def _render_single_floor(ax, floor: FloorSpec, spec: BuildingSpec,
                          floor_offset_x: float = 0) -> Tuple[float, float, float, float]:
    """Render one floor and return its bounding box (min_x, max_x, min_y, max_y)."""
    rooms = floor.rooms
    if not rooms:
        return (0, 0, 0, 0)

    all_x = [rm.x for rm in rooms] + [rm.x + rm.width for rm in rooms]
    all_y = [rm.y for rm in rooms] + [rm.y + rm.depth for rm in rooms]
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)

    # Draw rooms
    for rm in rooms:
        _draw_room(ax, rm, floor_offset_x)

    # Draw dimension lines for the overall building envelope
    _draw_dimension(ax, min_x + floor_offset_x, min_y,
                     max_x + floor_offset_x, min_y, offset=-0.7)
    _draw_dimension(ax, min_x + floor_offset_x, min_y,
                     min_x + floor_offset_x, max_y, offset=-0.7)

    # Draw individual room dimensions (width only, avoid clutter)
    for rm in rooms:
        rx = rm.x + floor_offset_x
        _draw_dimension(ax, rx, rm.y, rx + rm.width, rm.y, offset=-0.35,
                         label=f"{rm.width:.1f}")

    # Floor label
    floor_label = f"Floor {floor.floor_number}" if floor.floor_number > 0 else "Ground Floor"
    ax.text(
        (min_x + max_x) / 2 + floor_offset_x, max_y + 0.5,
        floor_label,
        ha="center", va="bottom",
        fontsize=10, fontweight="bold", color=TITLE_COLOR,
        zorder=7,
        bbox=dict(boxstyle="round,pad=0.3", fc="#F0F0F0", ec=WALL_COLOR, alpha=0.9),
    )

    return (min_x + floor_offset_x, max_x + floor_offset_x, min_y, max_y)


def render_floor_plan(spec: BuildingSpec, output_dir: str) -> str:
    """
    Render all floors to a single PNG file, side by side.
    Returns the absolute path to the saved PNG.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    out_path = os.path.join(output_dir, "floor_plan.png")

    if not spec.floors or all(not fl.rooms for fl in spec.floors):
        fig, ax = plt.subplots(figsize=(11.69, 8.27))
        ax.text(0.5, 0.5, "No rooms defined", transform=ax.transAxes,
                ha="center", va="center", fontsize=14)
        fig.savefig(out_path, dpi=200, bbox_inches="tight")
        plt.close(fig)
        return out_path

    # Calculate total width needed (all floors side by side)
    floor_widths = []
    gap = 3.0  # gap between floors
    for fl in spec.floors:
        if not fl.rooms:
            continue
        xs = [rm.x + rm.width for rm in fl.rooms]
        floor_widths.append(max(xs) - min(rm.x for rm in fl.rooms))

    n_floors = len([fl for fl in spec.floors if fl.rooms])
    total_w = sum(floor_widths) + gap * (n_floors - 1) if n_floors > 1 else (floor_widths[0] if floor_widths else 10)

    # Compute figure size
    max_depth = max(
        (max(rm.y + rm.depth for rm in fl.rooms) - min(rm.y for rm in fl.rooms))
        for fl in spec.floors if fl.rooms
    )

    fig_w = max(14, total_w * 1.3 + 4)
    fig_h = max(10, max_depth * 1.5 + 4)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    # Render each floor side by side
    offset_x = 0
    all_bounds = []
    for fl in sorted(spec.floors, key=lambda f: f.floor_number):
        if not fl.rooms:
            continue
        min_rm_x = min(rm.x for rm in fl.rooms)
        bounds = _render_single_floor(ax, fl, spec, floor_offset_x=offset_x - min_rm_x)
        all_bounds.append(bounds)
        fw = max(rm.x + rm.width for rm in fl.rooms) - min_rm_x
        offset_x += fw + gap

    # Set limits
    if all_bounds:
        g_min_x = min(b[0] for b in all_bounds) - 2
        g_max_x = max(b[1] for b in all_bounds) + 2
        g_min_y = min(b[2] for b in all_bounds) - 2
        g_max_y = max(b[3] for b in all_bounds) + 2
    else:
        g_min_x, g_max_x, g_min_y, g_max_y = -1, 11, -1, 9

    ax.set_xlim(g_min_x, g_max_x)
    ax.set_ylim(g_min_y, g_max_y)
    ax.set_aspect("equal")
    ax.axis("off")

    # Grid
    _draw_grid(ax, g_min_x, g_max_x, g_min_y, g_max_y)

    # Title
    fig.suptitle(
        f"AI Architect — Floor Plan  |  Style: {spec.style.title()}  |  "
        f"{len(spec.floors)} Floor{'s' if len(spec.floors) > 1 else ''}",
        fontsize=13, fontweight="bold", color=TITLE_COLOR, y=0.98,
    )

    # North arrow + scale bar
    _draw_north_arrow(ax, g_max_x - 1.2, g_min_y + 0.5)
    bar_len = min(5.0, (g_max_x - g_min_x) / 4)
    _draw_scale_bar(ax, g_min_x + 0.5, g_min_y + 0.3, scale_m=bar_len)

    # Legend
    legend_elements = [
        patches.Patch(facecolor=DOOR_COLOR, edgecolor="none", label="Door"),
        patches.Patch(facecolor=WINDOW_COLOR, edgecolor="none", label="Window"),
        patches.Patch(facecolor="#F5F5F0", edgecolor=WALL_COLOR, linewidth=1.5, label="Wall"),
        patches.Patch(facecolor="none", edgecolor=HATCH_COLOR, hatch="///", label="Wet Area"),
    ]
    ax.legend(handles=legend_elements, loc="lower right", fontsize=7,
              framealpha=0.9, edgecolor="#CCCCCC")

    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(out_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out_path
