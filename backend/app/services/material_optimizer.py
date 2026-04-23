"""
Material Optimizer — simulates alternative material combinations to reduce
construction costs and improve sustainability.

Suggests eco-friendly swaps (recycled concrete, bamboo, AAC blocks) with
cost-savings percentages and sustainability ratings.
"""
from __future__ import annotations
import logging
from typing import List

from app.models.schemas import (
    BuildingSpec, MaterialAlternative, OptimizationReport,
)

logger = logging.getLogger(__name__)

# ── Material Alternatives Database ────────────────────────────────────────────
# Each entry: (current, alternative, savings_pct, sustainability_score, description)
_ALTERNATIVES = [
    # Wall materials
    {
        "current_material": "Standard Clay Bricks",
        "alternative_material": "AAC Blocks (Autoclaved Aerated Concrete)",
        "component": "Walls",
        "cost_savings_pct": 15.0,
        "sustainability_score": 8,
        "pros": [
            "30% lighter than clay bricks — reduces structural load",
            "Better thermal insulation — lower HVAC costs",
            "Faster construction — larger block size",
            "Lower carbon footprint in manufacturing",
        ],
        "cons": [
            "Lower compressive strength than clay bricks",
            "Requires specialized adhesive mortar",
            "Not suitable for load-bearing beyond 3 stories without RCC frame",
        ],
    },
    {
        "current_material": "Standard Clay Bricks",
        "alternative_material": "Fly Ash Bricks",
        "component": "Walls",
        "cost_savings_pct": 20.0,
        "sustainability_score": 9,
        "pros": [
            "Uses industrial waste (fly ash) — circular economy",
            "Higher compressive strength than clay bricks",
            "Uniform size — less mortar needed",
            "Lower water absorption",
        ],
        "cons": [
            "Limited availability in some regions",
            "Slightly heavier than AAC blocks",
        ],
    },
    # Roofing
    {
        "current_material": "RCC Roof Slab",
        "alternative_material": "Pre-Engineered Metal Roofing",
        "component": "Roof",
        "cost_savings_pct": 25.0,
        "sustainability_score": 7,
        "pros": [
            "Significantly lighter — reduces foundation requirements",
            "Faster installation — reduces labor cost",
            "Excellent for large spans",
            "Recyclable material",
        ],
        "cons": [
            "Less thermal mass — may need insulation layer",
            "Noise during rain without insulation",
            "Limited aesthetic options for residential",
        ],
    },
    # Insulation
    {
        "current_material": "No Insulation (typical in South Asia)",
        "alternative_material": "Expanded Polystyrene (EPS) Wall Insulation",
        "component": "Insulation",
        "cost_savings_pct": -5.0,  # initial cost increase but long-term savings
        "sustainability_score": 6,
        "pros": [
            "Reduces cooling costs by up to 40%",
            "Pays for itself within 2–3 years",
            "Easy retrofit for existing buildings",
            "Reduces carbon footprint of building operation",
        ],
        "cons": [
            "Initial cost increase of ~5%",
            "Requires careful installation to avoid thermal bridges",
            "Not fire-resistant without treatment",
        ],
    },
    {
        "current_material": "Fiberglass Insulation",
        "alternative_material": "Bamboo Fiber Insulation",
        "component": "Insulation",
        "cost_savings_pct": 10.0,
        "sustainability_score": 10,
        "pros": [
            "100% renewable and biodegradable",
            "Comparable thermal performance to fiberglass",
            "No harmful microfibers",
            "Supports local bamboo farming economies",
        ],
        "cons": [
            "Less available in mainstream markets",
            "May require moisture barrier in humid climates",
        ],
    },
    # Concrete
    {
        "current_material": "Standard Portland Cement Concrete",
        "alternative_material": "Recycled Aggregate Concrete",
        "component": "Foundation & Slabs",
        "cost_savings_pct": 12.0,
        "sustainability_score": 8,
        "pros": [
            "Uses crushed demolition waste — reduces landfill",
            "Lower cost than virgin aggregates",
            "Comparable strength for most residential applications",
            "Reduces quarrying environmental impact",
        ],
        "cons": [
            "Slightly lower workability",
            "Quality depends on source material",
            "Not recommended for high-strength structural elements",
        ],
    },
    # Flooring
    {
        "current_material": "Imported Marble Flooring",
        "alternative_material": "Local Granite / Terrazzo",
        "component": "Flooring",
        "cost_savings_pct": 35.0,
        "sustainability_score": 7,
        "pros": [
            "Significantly lower cost than imported marble",
            "Extremely durable — outlasts marble",
            "Lower transportation carbon footprint",
            "Wide variety of colors and patterns",
        ],
        "cons": [
            "Heavier than some alternatives",
            "Perceived as less luxurious in some markets",
        ],
    },
    # Paint
    {
        "current_material": "Standard Acrylic Paint",
        "alternative_material": "Low-VOC Eco Paint",
        "component": "Finishes",
        "cost_savings_pct": -8.0,
        "sustainability_score": 9,
        "pros": [
            "Zero harmful volatile organic compounds",
            "Better indoor air quality — wellness architecture",
            "No toxic off-gassing",
            "Available in full color range",
        ],
        "cons": [
            "8–10% cost premium over standard paint",
            "May require additional coats for some colors",
        ],
    },
]


class MaterialOptimizer:
    """Suggests alternative materials for cost savings and sustainability."""

    def optimize(
        self,
        spec: BuildingSpec,
        budget: str = "medium",
    ) -> OptimizationReport:
        """Analyze the design and suggest material alternatives."""

        # Filter relevant alternatives based on building characteristics
        alternatives = []
        total_savings_pct = 0.0
        relevant_count = 0

        for alt_data in _ALTERNATIVES:
            # Filter based on budget — don't suggest cost-increasing options for low budget
            if budget == "low" and alt_data["cost_savings_pct"] < 0:
                continue

            alt = MaterialAlternative(
                current_material=alt_data["current_material"],
                alternative_material=alt_data["alternative_material"],
                component=alt_data["component"],
                cost_savings_pct=alt_data["cost_savings_pct"],
                sustainability_score=alt_data["sustainability_score"],
                pros=alt_data["pros"],
                cons=alt_data["cons"],
            )
            alternatives.append(alt)

            if alt_data["cost_savings_pct"] > 0:
                total_savings_pct += alt_data["cost_savings_pct"]
                relevant_count += 1

        # Average savings across positive-saving alternatives
        avg_savings = total_savings_pct / relevant_count if relevant_count > 0 else 0

        # Overall sustainability score
        if alternatives:
            avg_sustainability = sum(a.sustainability_score for a in alternatives) / len(alternatives)
        else:
            avg_sustainability = 5.0

        report = OptimizationReport(
            alternatives=alternatives,
            total_potential_savings_pct=round(avg_savings, 1),
            sustainability_score=round(avg_sustainability, 1),
            summary=(
                f"By adopting {relevant_count} material alternatives, you could save "
                f"approximately {avg_savings:.0f}% on construction costs while achieving "
                f"a sustainability score of {avg_sustainability:.1f}/10. "
                f"Key recommendations: use AAC/fly ash blocks for walls, "
                f"recycled aggregate for concrete, and local stone for flooring."
            ),
        )

        logger.info(
            "Material optimization: %d alternatives, ~%.0f%% avg savings",
            len(alternatives), avg_savings,
        )
        return report
