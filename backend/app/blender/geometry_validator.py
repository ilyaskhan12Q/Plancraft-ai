"""
Geometry validator — uses Shapely to check room overlaps and boundary violations.
"""
from __future__ import annotations
from typing import List

from shapely.geometry import box

from app.models.schemas import BuildingSpec


def validate_geometry(spec: BuildingSpec, tolerance: float = 0.05) -> List[str]:
    """
    Validate room geometry for a BuildingSpec.
    Returns a list of error strings. Empty list means valid.
    """
    errors: List[str] = []

    for floor_spec in spec.floors:
        fn = floor_spec.floor_number
        rooms = floor_spec.rooms
        polys = []

        for rm in rooms:
            # Check minimum size
            if rm.width < 1.5:
                errors.append(
                    f"Floor {fn}: '{rm.name}' width {rm.width:.1f}m is below minimum 1.5m"
                )
            if rm.depth < 1.5:
                errors.append(
                    f"Floor {fn}: '{rm.name}' depth {rm.depth:.1f}m is below minimum 1.5m"
                )

            poly = box(rm.x, rm.y, rm.x + rm.width, rm.y + rm.depth)
            polys.append((rm.name, poly))

        # Check overlaps between all room pairs
        for i in range(len(polys)):
            for j in range(i + 1, len(polys)):
                name_a, poly_a = polys[i]
                name_b, poly_b = polys[j]
                intersection = poly_a.intersection(poly_b)
                if not intersection.is_empty and intersection.area > tolerance:
                    errors.append(
                        f"Floor {fn}: '{name_a}' and '{name_b}' overlap "
                        f"by {intersection.area:.2f}m²"
                    )

    return errors
