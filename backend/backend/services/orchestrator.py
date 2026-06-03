"""
Unified pipeline orchestrator.
One call runs all 10 stages from raw image to structured analysis result.

Stages
------
1  Vision inference        VisionEngine
2  Grad-CAM++ heatmap      GradCAMEngine
3  Symbolic fact extraction SymbolicFactExtractor
4  Forward-chain inference  NSReasoningEngine
5  Temporal memory update   TemporalMemory
6  Trend analysis           TemporalMemory
7  Adaptive plan generation ContextEngine
8  Counterfactual reasoning generate_counterfactuals
9  Decision tree look-ahead build_tree
10 Human-adaptive explanations NSExplainer
"""

from __future__ import annotations
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List

import numpy as np
from loguru import logger

from backend.vision.model     import VisionEngine
from backend.xai.gradcam      import GradCAMEngine
from backend.reasoning.facts  import SymbolicFactExtractor, SymbolicFact
from backend.reasoning.engine import NSReasoningEngine, InferenceFact
from backend.memory.temporal  import TemporalMemory, MemoryEntry
from backend.planning.engine  import ContextEngine, TreatmentPlan
from backend.planning.counterfactual import generate_counterfactuals
from backend.planning.decision_tree  import (
    DecisionNode, build_tree, expected_leaf_urgency
)
from backend.services.explainer import NSExplainer
from backend.utils.image import ndarray_to_b64, heatmap_to_b64, resize_rgb


@dataclass
class AnalysisResult:
    request_id         : str
    processing_time_ms : float

    prediction         : Dict
    spatial_stats      : Dict
    heatmap            : np.ndarray
    gradcam_overlay    : np.ndarray

    facts              : List[SymbolicFact]
    inferences         : List[InferenceFact]
    trend              : Dict
    plan               : TreatmentPlan
    counterfactuals    : List[Dict]
    decision_tree      : DecisionNode
    expected_urgency   : float
    explanations       : Dict[str, str]

    # Base64 images for API response
    image_b64          : str = field(default="")
    gradcam_b64        : str = field(default="")
    heatmap_b64        : str = field(default="")


class Orchestrator:
    """
    All sub-engines are singletons — the model is loaded once and reused
    across every API request without re-initialisation overhead.
    """
    _instance: Orchestrator | None = None

    def __init__(self):
        logger.info("Initialising Orchestrator — loading all engines...")
        self.vision    = VisionEngine.get()
        self.gradcam   = GradCAMEngine.get()
        self.extractor = SymbolicFactExtractor()
        self.reasoner  = NSReasoningEngine.get()
        self.memory    = TemporalMemory.get()
        self.planner   = ContextEngine.get()
        self.explainer = NSExplainer.get()
        logger.info("Orchestrator ready")

    @classmethod
    def get(cls) -> Orchestrator:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def run(self, image_rgb: np.ndarray, image_path: str = "upload") -> AnalysisResult:
        t0         = time.perf_counter()
        request_id = str(uuid.uuid4())[:8]
        logger.info(f"[{request_id}] Pipeline start | path={image_path}")

        # 1. Vision
        prediction = self.vision.predict(image_rgb)
        logger.debug(f"[{request_id}] 1/10 vision: {prediction['disease']} ({prediction['confidence']:.3f})")

        # 2. Grad-CAM
        heatmap, gc_overlay  = self.gradcam.generate(image_rgb)
        spatial_stats        = self.gradcam.spatial_stats(heatmap)
        logger.debug(f"[{request_id}] 2/10 gradcam: spread={spatial_stats['infection_spread']}")

        # 3. Symbolic facts
        facts = self.extractor.extract(prediction, heatmap)
        logger.debug(f"[{request_id}] 3/10 facts: {len(facts)} extracted")

        # 4. Inference
        inferences  = self.reasoner.reason(facts, prediction["disease_type"])
        rules_fired = len(set(i.rule_fired for i in inferences))
        logger.debug(f"[{request_id}] 4/10 inference: {len(inferences)} facts | {rules_fired} rules")

        # 5. Memory update
        urgency_level = next((i.arguments[0] for i in inferences if i.predicate == "urgency_level"), "medium")
        urgency_score = float(next((i.arguments[0] for i in inferences if i.predicate == "urgency_score"), "1.5"))
        self.memory.add(MemoryEntry(
            timestamp        = datetime.now().isoformat(),
            image_path       = image_path,
            disease_type     = prediction["disease_type"],
            confidence       = prediction["confidence"],
            severity         = prediction["severity"],
            urgency_level    = urgency_level,
            urgency_score    = urgency_score,
            infection_spread = spatial_stats["infection_spread"],
            is_healthy       = prediction["is_healthy"],
            key_inferences   = [i.predicate for i in inferences[:8]],
        ))
        logger.debug(f"[{request_id}] 5/10 memory: {len(self.memory)} entries stored")

        # 6. Trend
        trend = self.memory.get_trend()
        logger.debug(f"[{request_id}] 6/10 trend: severity={trend['severity_trend']}")

        # 7. Plan
        plan = self.planner.generate_plan(facts, inferences, trend)
        logger.debug(f"[{request_id}] 7/10 plan: {len(plan.actions)} actions | urgency={plan.overall_urgency}")

        # 8. Counterfactuals
        counterfactuals = generate_counterfactuals(facts, inferences, plan, prediction)
        logger.debug(f"[{request_id}] 8/10 counterfactuals: {len(counterfactuals)} scenarios")

        # 9. Decision tree
        dt_root      = build_tree(plan, urgency_level)
        exp_urgency  = expected_leaf_urgency(dt_root)
        logger.debug(f"[{request_id}] 9/10 decision_tree: expected_urgency={exp_urgency:.3f}")

        # 10. Explanations
        explanations = self.explainer.render_all(
            prediction, facts, inferences, plan, counterfactuals, trend
        )
        logger.debug(f"[{request_id}] 10/10 explanations: 3 modes rendered")

        elapsed = round((time.perf_counter() - t0) * 1000, 1)
        logger.info(f"[{request_id}] Pipeline complete in {elapsed} ms")

        result = AnalysisResult(
            request_id         = request_id,
            processing_time_ms = elapsed,
            prediction         = prediction,
            spatial_stats      = spatial_stats,
            heatmap            = heatmap,
            gradcam_overlay    = gc_overlay,
            facts              = facts,
            inferences         = inferences,
            trend              = trend,
            plan               = plan,
            counterfactuals    = counterfactuals,
            decision_tree      = dt_root,
            expected_urgency   = round(exp_urgency, 3),
            explanations       = explanations,
        )

        # Encode images for JSON transport
        result.image_b64    = ndarray_to_b64(resize_rgb(image_rgb))
        result.gradcam_b64  = ndarray_to_b64(gc_overlay)
        result.heatmap_b64  = heatmap_to_b64(heatmap)

        return result
