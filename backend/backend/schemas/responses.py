"""
All API response models.
These are the public contract between the backend and the React frontend.
Field names and types must not change without a corresponding frontend update.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ── Shared leaf models ────────────────────────────────────────────────────────

class Top3Item(BaseModel):
    disease_class: str
    confidence: float


class SymbolicFact(BaseModel):
    predicate  : str
    arguments  : List[str]
    confidence : float
    source     : str     # vision_model | gradcam | derived


class InferenceResult(BaseModel):
    predicate  : str
    arguments  : List[str]
    confidence : float
    rule_fired : str
    support    : List[str]


class PlannedAction(BaseModel):
    step     : int
    action   : str
    category : str    # containment | chemical | physical | environmental | monitoring | verification
    urgency  : str    # critical | high | medium | low


class CounterfactualScenario(BaseModel):
    scenario         : str
    description      : str
    plan_delta       : int
    original_actions : int
    cf_actions       : int
    original_urgency : str
    cf_urgency       : str
    narrative        : str


class DecisionNode(BaseModel):
    step      : int
    action    : str
    state     : str
    urgency   : float
    probability: float
    is_leaf   : bool
    children  : List["DecisionNode"] = Field(default_factory=list)

DecisionNode.model_rebuild()


class TemporalTrend(BaseModel):
    severity_trend  : str
    urgency_trend   : str
    spread_trend    : str
    disease_stable  : bool
    n_observations  : int
    latest_urgency  : str
    latest_severity : str
    summary         : str


class Explanations(BaseModel):
    farmer     : str
    agronomist : str
    researcher : str


# ── Endpoint response models ──────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status      : str
    version     : str
    device      : str
    model_loaded: bool
    num_classes : int


class PredictionResponse(BaseModel):
    disease      : str
    plant        : str
    disease_type : str
    confidence   : float
    severity     : str    # high | medium | low
    is_healthy   : bool
    top3         : List[Top3Item]
    image_b64    : Optional[str] = None   # base64 PNG of the resized input


class XAIResponse(BaseModel):
    gradcam_overlay_b64 : str     # base64 PNG — Grad-CAM++ heatmap on image
    heatmap_b64         : str     # base64 PNG — raw jet-colourmap heatmap
    infection_spread    : str     # localised | moderate | widespread
    focus_score         : float
    activation_entropy  : float


class ReasoningResponse(BaseModel):
    symbolic_facts     : List[SymbolicFact]
    inferences         : List[InferenceResult]
    urgency_level      : str
    urgency_score      : float
    spread_risk        : str
    treatment_class    : str
    requires_isolation : bool
    rules_fired        : int


class PlanResponse(BaseModel):
    disease_type        : str
    overall_urgency     : str
    actions             : List[PlannedAction]
    adaptations         : List[Dict[str, str]]
    escalation_flag     : bool
    confidence_note     : str
    monitoring_interval : str
    inference_trace     : List[str]


class MemoryResponse(BaseModel):
    n_observations         : int
    capacity               : int
    trend                  : TemporalTrend
    monitoring_recommendation: str
    entries                : List[Dict[str, Any]]


class KnowledgeGraphResponse(BaseModel):
    num_nodes     : int
    num_edges     : int
    node_types    : Dict[str, int]
    edge_relations: Dict[str, int]


class FullAnalysisResponse(BaseModel):
    """
    Primary endpoint response — one image in, complete analysis out.
    Every field the React frontend will ever need is here.
    """
    request_id          : str
    processing_time_ms  : float

    prediction   : PredictionResponse
    xai          : XAIResponse
    reasoning    : ReasoningResponse
    plan         : PlanResponse
    counterfactuals: List[CounterfactualScenario]
    decision_tree: DecisionNode
    expected_urgency: float
    explanations : Explanations
    trend        : TemporalTrend


class ErrorResponse(BaseModel):
    detail     : str
    error_type : str
