"""
Construction Cost Estimator — calculates real-world construction costs
in PKR and USD with Bill of Quantities (BoQ).

Based on 2026 South Asian / Pakistani construction data:
- Low:    PKR 2,800–3,500 / sqft
- Medium: PKR 3,500–5,000 / sqft
- High:   PKR 5,000–8,000 / sqft
- Luxury: PKR 8,000–15,000 / sqft

USD rates are converted at ~1 USD = 280 PKR (2026 avg).
"""
from __future__ import annotations
import logging
from typing import Optional

from app.models.schemas import (
    BuildingSpec, BillOfQuantities, CostReport,
)

logger = logging.getLogger(__name__)

# ── Cost rates per sqft in PKR (2026 estimates) ───────────────────────────────
_COST_RATES_PKR = {
    "low":    {"low": 2800, "mid": 3200, "high": 3500},
    "medium": {"low": 3500, "mid": 4200, "high": 5000},
    "high":   {"low": 5000, "mid": 6500, "high": 8000},
    "luxury": {"low": 8000, "mid": 11000, "high": 15000},
}

# ── Material quantities per sqft (approximate South Asian standards) ──────────
_MATERIAL_PER_SQFT = {
    "bricks":          8,       # number of bricks per sqft
    "cement_bags_50kg": 0.04,   # 50 kg bags per sqft
    "steel_kg":        0.6,     # reinforcement steel in kg
    "paint_litres":    0.18,    # interior + exterior paint
    "sand_m3":         0.012,   # sand in cubic meters
    "aggregate_m3":    0.008,   # coarse aggregate in m³
    "tiles_sqft":      0.3,     # floor tiles in sqft (for tiled areas)
}

# ── PKR to USD conversion (2026 average) ──────────────────────────────────────
PKR_TO_USD = 1 / 280.0

# ── Regional multipliers ─────────────────────────────────────────────────────
_REGION_MULTIPLIER = {
    "south_asian": 1.0,
    "middle_east": 1.6,
    "europe": 3.2,
    "north_america": 3.5,
    "east_asia": 2.0,
}


class CostEstimator:
    """Calculate construction cost estimates from a BuildingSpec."""

    def estimate(
        self,
        spec: BuildingSpec,
        budget: str = "medium",
        region: str = "south_asian",
    ) -> CostReport:
        """Compute full cost estimate with Bill of Quantities."""

        # Total area
        total_area_m2 = sum(
            rm.width * rm.depth
            for fl in spec.floors
            for rm in fl.rooms
        )
        total_area_sqft = total_area_m2 * 10.764  # 1 m² = 10.764 sqft

        # Per-floor breakdown
        floor_areas = {}
        for fl in spec.floors:
            fl_area = sum(rm.width * rm.depth for rm in fl.rooms)
            floor_areas[f"Floor {fl.floor_number}"] = round(fl_area * 10.764, 1)

        # Cost rates
        budget_key = budget if budget in _COST_RATES_PKR else "medium"
        rates = _COST_RATES_PKR[budget_key]
        region_mult = _REGION_MULTIPLIER.get(region, 1.0)

        cost_pkr_low = round(total_area_sqft * rates["low"] * region_mult)
        cost_pkr_mid = round(total_area_sqft * rates["mid"] * region_mult)
        cost_pkr_high = round(total_area_sqft * rates["high"] * region_mult)

        # PKR → USD
        cost_usd_low = round(cost_pkr_low * PKR_TO_USD)
        cost_usd_mid = round(cost_pkr_mid * PKR_TO_USD)
        cost_usd_high = round(cost_pkr_high * PKR_TO_USD)

        # Bill of Quantities
        boq = BillOfQuantities(
            bricks=round(total_area_sqft * _MATERIAL_PER_SQFT["bricks"]),
            cement_bags_50kg=round(total_area_sqft * _MATERIAL_PER_SQFT["cement_bags_50kg"], 1),
            steel_kg=round(total_area_sqft * _MATERIAL_PER_SQFT["steel_kg"], 1),
            paint_litres=round(total_area_sqft * _MATERIAL_PER_SQFT["paint_litres"], 1),
            sand_m3=round(total_area_sqft * _MATERIAL_PER_SQFT["sand_m3"], 2),
            aggregate_m3=round(total_area_sqft * _MATERIAL_PER_SQFT["aggregate_m3"], 2),
            tiles_sqft=round(total_area_sqft * _MATERIAL_PER_SQFT["tiles_sqft"], 1),
        )

        report = CostReport(
            total_area_m2=round(total_area_m2, 2),
            total_area_sqft=round(total_area_sqft, 1),
            floor_areas=floor_areas,
            budget_tier=budget_key,
            region=region,
            cost_pkr_low=cost_pkr_low,
            cost_pkr_mid=cost_pkr_mid,
            cost_pkr_high=cost_pkr_high,
            cost_usd_low=cost_usd_low,
            cost_usd_mid=cost_usd_mid,
            cost_usd_high=cost_usd_high,
            bill_of_quantities=boq,
        )

        logger.info(
            "Cost estimate: %.0f sqft, PKR %s–%s (%s tier)",
            total_area_sqft, f"{cost_pkr_low:,}", f"{cost_pkr_high:,}", budget_key,
        )
        return report
