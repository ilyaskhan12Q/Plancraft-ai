"""
All Pydantic v2 models for AI Architect backend.
"""
from __future__ import annotations
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, model_validator
import uuid


# ─────────────────────────── Input Models ────────────────────────────────────

class PlotSpec(BaseModel):
    length: float = Field(..., gt=0, description="Plot length in given units")
    width: float = Field(..., gt=0, description="Plot width in given units")
    unit: str = Field(default="meters", pattern="^(meters|feet)$")
    floors: int = Field(default=1, ge=1, le=10)
    orientation: str = Field(default="north", description="Primary road-facing direction")


class RoomRequirements(BaseModel):
    bedrooms: int = Field(default=3, ge=1, le=10)
    bathrooms: int = Field(default=2, ge=1, le=10)
    living_room: bool = True
    kitchen: bool = True
    dining: bool = False
    garage: bool = False
    study: bool = False
    servant_quarter: bool = False


class GenerateRequest(BaseModel):
    plot: PlotSpec
    rooms: RoomRequirements = Field(default_factory=RoomRequirements)
    preferred_style: str = Field(default="modern", description="Architectural style")
    budget: str = Field(default="medium", pattern="^(low|medium|high|luxury)$")
    region: str = Field(default="south_asian")
    description: Optional[str] = Field(default=None, max_length=1000)
    site_photo_key: Optional[str] = None
    style_photo_key: Optional[str] = None
    sketch_photo_key: Optional[str] = None


# ─────────────────────────── Building Spec ────────────────────────────────────

class RoomSpec(BaseModel):
    name: str
    width: float = Field(..., gt=0)
    depth: float = Field(..., gt=0)
    x: float = 0.0
    y: float = 0.0
    floor: int = 0
    has_window: bool = True
    has_door: bool = True
    door_wall: str = Field(default="south", pattern="^(north|south|east|west)$")


class FloorSpec(BaseModel):
    floor_number: int = 0
    height: float = Field(default=3.0, description="Floor-to-ceiling height in meters")
    rooms: List[RoomSpec] = Field(default_factory=list)


class CameraSpec(BaseModel):
    pos: List[float] = Field(default=[20.0, -20.0, 15.0], min_length=3, max_length=3)
    look_at: List[float] = Field(default=[0.0, 0.0, 3.0], min_length=3, max_length=3)
    lens: float = Field(default=35.0)


class BuildingSpec(BaseModel):
    style: str = "modern"
    floors: List[FloorSpec] = Field(default_factory=list)
    exterior_color: str = "#F5F5F0"
    roof_type: str = Field(default="flat", pattern="^(flat|gable|hip|shed|mansard)$")
    roof_color: str = "#808080"
    window_type: str = Field(default="casement", pattern="^(casement|sliding|fixed|bay)$")
    door_style: str = Field(default="modern_panel")
    facade_material: str = Field(default="plaster")
    camera: CameraSpec = Field(default_factory=CameraSpec)
    site_notes: Optional[str] = None

    @model_validator(mode="after")
    def ensure_floors(self) -> "BuildingSpec":
        if not self.floors:
            self.floors = [FloorSpec(floor_number=0)]
        return self


# ─────────────────────────── Job / Status ─────────────────────────────────────

class VariantResult(BaseModel):
    variant: str
    floorplan_url: Optional[str] = None
    render_url: Optional[str] = None
    model_url: Optional[str] = None
    stl_url: Optional[str] = None


class JobStatus(BaseModel):
    job_id: str
    status: str = "pending"          # pending | running | done | failed
    progress: float = 0.0            # 0.0 – 1.0
    stage: str = "Queued"
    error: Optional[str] = None
    variants: List[VariantResult] = Field(default_factory=list)
    spec: Optional[Dict[str, Any]] = None


# ─────────────────────────── Vision Analysis ─────────────────────────────────

class SiteAnalysis(BaseModel):
    terrain: Optional[str] = None
    vegetation: Optional[str] = None
    road_facing: Optional[str] = None
    constraints: Optional[str] = None
    raw: Optional[str] = None


class StyleAnalysis(BaseModel):
    detected_style: Optional[str] = None
    colors: Optional[List[str]] = Field(default_factory=list)
    features: Optional[List[str]] = Field(default_factory=list)
    raw: Optional[str] = None


# ─────────────────────────── Export ───────────────────────────────────────────

class ExportLinks(BaseModel):
    job_id: str
    floorplan: Optional[str] = None
    render: Optional[str] = None
    model: Optional[str] = None
    stl: Optional[str] = None


# ─────────────────────────── Customize ───────────────────────────────────────

class CustomizeRequest(BaseModel):
    exterior_color: Optional[str] = None
    roof_color: Optional[str] = None
    roof_type: Optional[str] = None
    facade_material: Optional[str] = None
    window_type: Optional[str] = None


# ─────────────────────────── Concept Art ─────────────────────────────────────

class ConceptArtRequest(BaseModel):
    style: str = "modern"
    description: str = ""
    inspirations: List[str] = Field(default_factory=list)
    mood: Optional[str] = None
    building_type: str = "residential"
    num_concepts: int = 4

class ConceptIdea(BaseModel):
    name: str
    description: str
    features: List[str] = Field(default_factory=list)
    color_palette: List[str] = Field(default_factory=list)
    materials: List[str] = Field(default_factory=list)
    render_prompt: str

class ConceptArtResponse(BaseModel):
    concepts: List[ConceptIdea] = Field(default_factory=list)
    raw_response: str


# ─────────────────────────── Interior Design ─────────────────────────────────

class InteriorRoomRequest(BaseModel):
    name: str
    style: str = "modern"
    width: float
    depth: float
    floor: int

class InteriorDesignRequest(BaseModel):
    rooms: List[InteriorRoomRequest]
    overall_style: str = "modern"

class RoomInterior(BaseModel):
    room_name: str
    furniture: List[str] = Field(default_factory=list)
    color_scheme: Dict[str, str] = Field(default_factory=dict)
    materials: Dict[str, str] = Field(default_factory=dict)
    lighting: List[str] = Field(default_factory=list)
    decor_style: str
    estimated_budget_usd: int

class InteriorDesignResponse(BaseModel):
    rooms: List[RoomInterior] = Field(default_factory=list)
    raw_response: str


# ─────────────────────────── Critique ────────────────────────────────────────

class CritiquePoint(BaseModel):
    category: str
    score: int
    feedback: str
    suggestion: str

class DesignCritique(BaseModel):
    overall_score: float
    overall_verdict: str
    points: List[CritiquePoint] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    top_recommendations: List[str] = Field(default_factory=list)
    raw_response: str


# ─────────────────────────── Cost Estimation & Materials ─────────────────────

class BillOfQuantities(BaseModel):
    bricks: int
    cement_bags_50kg: float
    steel_kg: float
    paint_litres: float
    sand_m3: float
    aggregate_m3: float
    tiles_sqft: float

class CostReport(BaseModel):
    total_area_m2: float
    total_area_sqft: float
    floor_areas: Dict[str, float]
    budget_tier: str
    region: str
    cost_pkr_low: int
    cost_pkr_mid: int
    cost_pkr_high: int
    cost_usd_low: int
    cost_usd_mid: int
    cost_usd_high: int
    bill_of_quantities: BillOfQuantities

class MaterialAlternative(BaseModel):
    current_material: str
    alternative_material: str
    component: str
    cost_savings_pct: float
    sustainability_score: int
    pros: List[str]
    cons: List[str]

class OptimizationReport(BaseModel):
    alternatives: List[MaterialAlternative]
    total_potential_savings_pct: float
    sustainability_score: float
    summary: str
