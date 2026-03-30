"""
Cost Estimator service.
Calculates construction cost and bill of quantities from a BuildingSpec.
All rates are in PKR (Pakistani Rupees) as of 2025-2026.
"""
from __future__ import annotations
import math
from app.models.schemas import BuildingSpec, CostEstimate, BillOfQuantities


# ── Construction cost rates per sqft (PKR) ────────────────────────────────────
# Source: Pakistan Engineering Council & market surveys 2025
_RATE_LOW_PKR_PER_SQFT  = 3_200   # basic load-bearing brick
_RATE_MID_PKR_PER_SQFT  = 4_800   # RCC frame, standard finish
_RATE_HIGH_PKR_PER_SQFT = 7_500   # RCC, premium finish

# USD exchange rate (approx.)
_PKR_TO_USD = 280.0


def _total_covered_area_sqm(spec: BuildingSpec) -> float:
    """Sum area of all rooms across all floors."""
    total = 0.0
    for floor in spec.floors:
        for room in floor.rooms:
            total += room.width * room.depth
    return total


def estimate(spec: BuildingSpec) -> CostEstimate:
    """
    Generate a cost estimate and bill of quantities for a BuildingSpec.
    Returns a CostEstimate model.
    """
    area_sqm = _total_covered_area_sqm(spec)
    area_sqft = area_sqm * 10.7639

    # Construction cost ranges
    cost_low  = int(area_sqft * _RATE_LOW_PKR_PER_SQFT)
    cost_mid  = int(area_sqft * _RATE_MID_PKR_PER_SQFT)
    cost_high = int(area_sqft * _RATE_HIGH_PKR_PER_SQFT)
    cost_usd  = int(cost_mid / _PKR_TO_USD)

    # ── Bill of Quantities (engineering formulas) ──────────────────────────────
    # Bricks: ~500 standard bricks per m² of wall area
    # Assume avg wall height = 3m, perimeter ~ 4 * sqrt(area_sqm) * num_floors
    num_floors = len(spec.floors) or 1
    perimeter_m = 4 * math.sqrt(area_sqm / num_floors) * num_floors
    wall_area_sqm = perimeter_m * 3.0                  # rough wall area
    bricks = int(wall_area_sqm * 500 * 0.60)           # 60% are bricks (rest openings)

    # Cement: ~0.4 bags per sqft of covered area (structure + finishing)
    cement_bags = int(area_sqft * 0.40)

    # Steel: ~4 kg per sqft for RCC construction
    steel_kg = int(area_sqft * 4.0)

    # Paint: 1 liter covers ~10 sqft (2 coats interior + exterior)
    total_paintable = area_sqft * 3.5  # walls + ceiling approximation
    paint_liters = int(total_paintable / 10)

    # Sand: ~0.05 cubic meters per sqft
    sand_cum = round(area_sqft * 0.05, 1)

    boq = BillOfQuantities(
        bricks=bricks,
        cement_bags=cement_bags,
        steel_kg=steel_kg,
        paint_liters=paint_liters,
        sand_cubic_meters=sand_cum,
    )

    return CostEstimate(
        covered_area_sqm=round(area_sqm, 1),
        covered_area_sqft=round(area_sqft, 0),
        cost_pkr_low=cost_low,
        cost_pkr_mid=cost_mid,
        cost_pkr_high=cost_high,
        cost_usd_mid=cost_usd,
        bill_of_quantities=boq,
    )
