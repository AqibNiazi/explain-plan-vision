"""
All API endpoints.
Every route is documented so FastAPI auto-generates accurate Swagger UI.
"""

from __future__ import annotations
import numpy as np
from fastapi import APIRouter, File, HTTPException, UploadFile, status
from loguru import logger

from backend.config  import settings
from backend.schemas.responses import (
    HealthResponse, PredictionResponse, XAIResponse,
    PlanResponse, FullAnalysisResponse, MemoryResponse,
    KnowledgeGraphResponse, ReasoningResponse,
    Top3Item, SymbolicFact, InferenceResult, PlannedAction,
    CounterfactualScenario, DecisionNode as DecisionNodeSchema,
    TemporalTrend, Explanations, ErrorResponse,
)
from backend.utils.image import (
    load_image_rgb_from_bytes, validate_upload,
    ndarray_to_b64, heatmap_to_b64, resize_rgb,
)
from backend.vision.model     import VisionEngine
from backend.xai.gradcam      import GradCAMEngine
from backend.memory.temporal  import TemporalMemory
from backend.reasoning.knowledge_graph import DiseaseKnowledgeGraph
from backend.services.orchestrator     import Orchestrator

router = APIRouter()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _read_image(file: UploadFile) -> np.ndarray:
    data = file.file.read()
    try:
        validate_upload(file.filename or "upload.jpg", len(data))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    try:
        return load_image_rgb_from_bytes(data)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))


def _node_schema(node) -> DecisionNodeSchema:
    return DecisionNodeSchema(
        step=node.step, action=node.action, state=node.state_description,
        urgency=node.expected_urgency, probability=node.probability,
        is_leaf=node.is_leaf,
        children=[_node_schema(c) for c in node.children],
    )


# ── Health ────────────────────────────────────────────────────────────────────

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Server liveness and model status",
    tags=["System"],
)
def health():
    """Returns server status, model load state, and device information."""
    try:
        ve    = VisionEngine.get()
        ok    = True
        n_cls = ve.num_classes
    except Exception:
        ok    = False
        n_cls = 0
    return HealthResponse(
        status       = "ok" if ok else "model_not_loaded",
        version      = settings.app_version,
        device       = settings.device,
        model_loaded = ok,
        num_classes  = n_cls,
    )


# ── Predict ───────────────────────────────────────────────────────────────────

@router.post(
    "/predict",
    response_model=PredictionResponse,
    summary="Disease classification from a leaf image",
    tags=["Analysis"],
)
def predict(
    file: UploadFile = File(..., description="Leaf image (JPG/PNG/WebP, max 10 MB)"),
):
    """
    Runs EfficientNet-B0 inference and returns the predicted disease,
    confidence, severity, and top-3 alternatives.
    """
    image = _read_image(file)
    ve    = VisionEngine.get()
    pred  = ve.predict(image)
    return PredictionResponse(
        disease      = pred["disease"],
        plant        = pred["plant"],
        disease_type = pred["disease_type"],
        confidence   = pred["confidence"],
        severity     = pred["severity"],
        is_healthy   = pred["is_healthy"],
        top3         = [Top3Item(**t) for t in pred["top3"]],
        image_b64    = ndarray_to_b64(resize_rgb(image)),
    )


# ── XAI ──────────────────────────────────────────────────────────────────────

@router.post(
    "/explain",
    response_model=XAIResponse,
    summary="Grad-CAM++ spatial explanation",
    tags=["Analysis"],
)
def explain(
    file: UploadFile = File(..., description="Leaf image"),
):
    """
    Returns Grad-CAM++ heatmap and overlay images (base64 PNG) showing
    which spatial regions of the leaf drove the prediction.
    """
    image = _read_image(file)
    ge    = GradCAMEngine.get()
    hm, overlay = ge.generate(image)
    stats = ge.spatial_stats(hm)
    return XAIResponse(
        gradcam_overlay_b64 = ndarray_to_b64(overlay),
        heatmap_b64         = heatmap_to_b64(hm),
        infection_spread    = stats["infection_spread"],
        focus_score         = stats["focus_score"],
        activation_entropy  = stats["activation_entropy"],
    )


# ── Plan ──────────────────────────────────────────────────────────────────────

@router.post(
    "/plan",
    response_model=PlanResponse,
    summary="Dynamically adapted treatment plan",
    tags=["Analysis"],
)
def plan(
    file: UploadFile = File(..., description="Leaf image"),
):
    """
    Runs the full pipeline up to and including plan generation.
    Returns a prioritised, step-numbered action sequence adapted to
    the current disease state and temporal trend.
    """
    image  = _read_image(file)
    result = Orchestrator.get().run(image, image_path=file.filename or "upload")
    p      = result.plan
    return PlanResponse(
        disease_type        = p.disease_type,
        overall_urgency     = p.overall_urgency,
        actions             = [PlannedAction(**{k: v for k, v in a.items() if k != "priority"})
                               for a in p.actions],
        adaptations         = p.adaptations,
        escalation_flag     = p.escalation_flag,
        confidence_note     = p.confidence_note,
        monitoring_interval = p.monitoring_interval,
        inference_trace     = p.inference_trace,
    )


# ── Full Analysis ─────────────────────────────────────────────────────────────

@router.post(
    "/full-analysis",
    response_model=FullAnalysisResponse,
    summary="Complete 10-stage neuro-symbolic analysis",
    tags=["Analysis"],
)
def full_analysis(
    file: UploadFile = File(..., description="Leaf image (JPG/PNG/WebP, max 10 MB)"),
):
    """
    The primary endpoint for the React frontend.

    Runs the complete pipeline:

    Vision → Grad-CAM++ → Symbolic Facts → Knowledge Graph Inference
    → Temporal Memory → Adaptive Plan → Counterfactuals
    → Decision Tree → Human-Adaptive Explanations

    Returns a single JSON object containing every field the frontend needs.
    Processing time is typically 1–5 s on CPU, under 1 s on GPU.
    """
    image  = _read_image(file)
    r      = Orchestrator.get().run(image, image_path=file.filename or "upload")
    pred   = r.prediction
    p      = r.plan
    facts  = r.facts
    infs   = r.inferences
    trend  = r.trend

    fm     = {f.predicate: f.arguments[0] for f in facts}
    im     = {}
    for i in infs:
        im.setdefault(i.predicate, i.arguments[0])

    pred_out = PredictionResponse(
        disease=pred["disease"], plant=pred["plant"], disease_type=pred["disease_type"],
        confidence=pred["confidence"], severity=pred["severity"], is_healthy=pred["is_healthy"],
        top3=[Top3Item(**t) for t in pred["top3"]], image_b64=r.image_b64,
    )
    xai_out = XAIResponse(
        gradcam_overlay_b64 = r.gradcam_b64,
        heatmap_b64         = r.heatmap_b64,
        infection_spread    = r.spatial_stats["infection_spread"],
        focus_score         = r.spatial_stats["focus_score"],
        activation_entropy  = r.spatial_stats["activation_entropy"],
    )
    reason_out = ReasoningResponse(
        symbolic_facts     = [SymbolicFact(predicate=f.predicate, arguments=f.arguments,
                               confidence=f.confidence, source=f.source) for f in facts],
        inferences         = [InferenceResult(predicate=i.predicate, arguments=i.arguments,
                               confidence=i.confidence, rule_fired=i.rule_fired,
                               support=i.support) for i in infs],
        urgency_level      = im.get("urgency_level", "unknown"),
        urgency_score      = float(im.get("urgency_score", "0")),
        spread_risk        = fm.get("spread_risk", "unknown"),
        treatment_class    = fm.get("treatment_class", "unknown"),
        requires_isolation = fm.get("requires_isolation", "False") == "True",
        rules_fired        = len(set(i.rule_fired for i in infs)),
    )
    plan_out = PlanResponse(
        disease_type        = p.disease_type,
        overall_urgency     = p.overall_urgency,
        actions             = [PlannedAction(**{k: v for k, v in a.items() if k != "priority"})
                               for a in p.actions],
        adaptations         = p.adaptations,
        escalation_flag     = p.escalation_flag,
        confidence_note     = p.confidence_note,
        monitoring_interval = p.monitoring_interval,
        inference_trace     = p.inference_trace,
    )
    trend_out = TemporalTrend(
        severity_trend   = trend.get("severity_trend", "unknown"),
        urgency_trend    = trend.get("urgency_trend", "unknown"),
        spread_trend     = trend.get("spread_trend", "unknown"),
        disease_stable   = trend.get("disease_stable", True),
        n_observations   = trend.get("n_observations", 1),
        latest_urgency   = trend.get("latest_urgency", "unknown"),
        latest_severity  = trend.get("latest_severity", "unknown"),
        summary          = trend.get("summary", ""),
    )
    return FullAnalysisResponse(
        request_id          = r.request_id,
        processing_time_ms  = r.processing_time_ms,
        prediction          = pred_out,
        xai                 = xai_out,
        reasoning           = reason_out,
        plan                = plan_out,
        counterfactuals     = [CounterfactualScenario(**cf) for cf in r.counterfactuals],
        decision_tree       = _node_schema(r.decision_tree),
        expected_urgency    = r.expected_urgency,
        explanations        = Explanations(**r.explanations),
        trend               = trend_out,
    )


# ── Memory ────────────────────────────────────────────────────────────────────

@router.get(
    "/memory",
    response_model=MemoryResponse,
    summary="Temporal memory state and trend analysis",
    tags=["Memory"],
)
def get_memory():
    """Returns all stored observations, trend signals, and monitoring recommendation."""
    mem   = TemporalMemory.get()
    trend = mem.get_trend()
    return MemoryResponse(
        n_observations           = len(mem),
        capacity                 = mem.capacity,
        trend                    = TemporalTrend(**trend),
        monitoring_recommendation= mem.recommend_monitoring(),
        entries                  = mem.to_list(),
    )


@router.delete(
    "/memory",
    summary="Clear temporal memory",
    tags=["Memory"],
)
def clear_memory():
    """Resets the temporal memory to empty. Use between separate monitoring sessions."""
    TemporalMemory.get().clear()
    return {"status": "cleared", "n_observations": 0}


# ── Knowledge Graph ────────────────────────────────────────────────────────────

@router.get(
    "/knowledge-graph",
    response_model=KnowledgeGraphResponse,
    summary="Knowledge graph metadata",
    tags=["System"],
)
def knowledge_graph():
    """Returns node/edge counts and type breakdown of the disease knowledge graph."""
    kg = DiseaseKnowledgeGraph.get()
    G  = kg.G
    rels = {}
    for _, _, d in G.edges(data=True):
        r = d.get("relation", "?")
        rels[r] = rels.get(r, 0) + 1
    ntypes = {}
    for _, d in G.nodes(data=True):
        t = d.get("type", "?")
        ntypes[t] = ntypes.get(t, 0) + 1
    return KnowledgeGraphResponse(
        num_nodes      = G.number_of_nodes(),
        num_edges      = G.number_of_edges(),
        node_types     = ntypes,
        edge_relations = rels,
    )
