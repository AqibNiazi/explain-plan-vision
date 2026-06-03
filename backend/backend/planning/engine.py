"""
Adaptive treatment plan generator.
Merges base action templates with context adaptations driven by
symbolic facts, inference results, and temporal trend signals.
"""

from __future__ import annotations
import copy
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List

from loguru import logger
from backend.config import settings
from backend.reasoning.facts import SymbolicFact
from backend.reasoning.engine import InferenceFact


BASE_ACTIONS: Dict[str, List[Dict]] = {
    "fungicide": [
        {"action": "Apply copper-based or chlorothalonil fungicide",
         "category": "chemical",     "urgency": "high",   "priority": 8.0},
        {"action": "Remove and dispose of infected leaves",
         "category": "physical",     "urgency": "high",   "priority": 7.5},
        {"action": "Switch to drip irrigation — keep foliage dry",
         "category": "environmental","urgency": "medium", "priority": 6.0},
    ],
    "systemic_fungicide": [
        {"action": "Immediately isolate affected plants from the rest of the crop",
         "category": "containment",  "urgency": "critical","priority": 10.0},
        {"action": "Apply systemic fungicide (metalaxyl or mancozeb) within 24 hours",
         "category": "chemical",     "urgency": "critical","priority": 9.5},
        {"action": "Remove and destroy all infected material — do not compost",
         "category": "physical",     "urgency": "high",   "priority": 9.0},
        {"action": "Eliminate overhead irrigation entirely",
         "category": "environmental","urgency": "high",   "priority": 8.5},
        {"action": "Apply preventive fungicide spray to neighbouring plants",
         "category": "containment",  "urgency": "high",   "priority": 8.0},
    ],
    "bactericide": [
        {"action": "Apply copper-based bactericide",
         "category": "chemical",     "urgency": "high",   "priority": 8.5},
        {"action": "Remove infected leaves and disinfect tools between plants",
         "category": "physical",     "urgency": "high",   "priority": 8.0},
        {"action": "Avoid working in the field during wet conditions",
         "category": "environmental","urgency": "medium", "priority": 6.0},
    ],
    "vector_control": [
        {"action": "Remove and destroy infected plants — no chemical cure exists",
         "category": "containment",  "urgency": "critical","priority": 10.0},
        {"action": "Apply systemic insecticide (imidacloprid) to eliminate the vector",
         "category": "chemical",     "urgency": "critical","priority": 9.5},
        {"action": "Install yellow sticky traps to monitor vector population",
         "category": "monitoring",   "urgency": "high",   "priority": 8.0},
        {"action": "Use reflective mulch to deter whitefly vectors",
         "category": "environmental","urgency": "medium", "priority": 6.5},
    ],
    "miticide": [
        {"action": "Apply miticide (abamectin or bifenazate)",
         "category": "chemical",     "urgency": "high",   "priority": 8.5},
        {"action": "Increase relative humidity — spider mites thrive in dry conditions",
         "category": "environmental","urgency": "high",   "priority": 8.0},
        {"action": "Remove and destroy heavily infested leaves",
         "category": "physical",     "urgency": "medium", "priority": 7.0},
    ],
    "monitoring_only": [
        {"action": "Continue current cultural practices",
         "category": "monitoring",   "urgency": "low",    "priority": 2.0},
        {"action": "Inspect weekly as part of routine crop monitoring",
         "category": "monitoring",   "urgency": "low",    "priority": 1.5},
    ],
    "expert_consultation": [
        {"action": "Seek expert agronomist verification before applying any treatment",
         "category": "verification", "urgency": "high",   "priority": 9.0},
        {"action": "Photograph symptoms and submit to local extension service",
         "category": "verification", "urgency": "high",   "priority": 8.5},
    ],
}


@dataclass
class TreatmentPlan:
    disease_type        : str
    actions             : List[Dict]
    adaptations         : List[Dict]
    inference_trace     : List[str]
    monitoring_interval : str
    escalation_flag     : bool
    confidence_note     : str
    overall_urgency     : str


class ContextEngine:
    """Singleton adaptive plan generator."""

    _instance: ContextEngine | None = None

    @classmethod
    def get(cls) -> ContextEngine:
        if cls._instance is None:
            cls._instance = cls()
            logger.info("ContextEngine ready")
        return cls._instance

    def generate_plan(
        self,
        facts      : List[SymbolicFact],
        inferences : List[InferenceFact],
        trend      : Dict,
    ) -> TreatmentPlan:

        fm      = {f.predicate: f.arguments[0] for f in facts}
        inf_map : Dict[str, List[str]] = defaultdict(list)
        for i in inferences:
            inf_map[i.predicate].append(i.arguments[0])

        treatment_class = fm.get("treatment_class", "expert_consultation")
        conf_fact       = next((f for f in facts if f.predicate == "disease_is"), None)
        confidence      = conf_fact.confidence if conf_fact else 0.8

        actions     = copy.deepcopy(BASE_ACTIONS.get(treatment_class,
                      BASE_ACTIONS["expert_consultation"]))
        adaptations : List[Dict] = []
        trace       : List[str]  = []

        # 1. Low confidence gate
        if confidence < settings.confidence_gate:
            actions.insert(0, {
                "action"  : f"Seek expert verification — model confidence is only {confidence:.1%}",
                "category": "verification", "urgency": "high", "priority": 10.5,
            })
            adaptations.append({"type": "confidence_gate", "detail": f"{confidence:.3f}"})
            trace.append(f"confidence_gate: {confidence:.3f} < {settings.confidence_gate}")

        # 2. Trend escalation
        if trend.get("severity_trend") == "increasing":
            for a in actions:
                if a["urgency"] == "medium":
                    a["urgency"]   = "high"
                    a["priority"] += 1.5
            adaptations.append({"type": "trend_escalation", "detail": "severity_increasing"})
            trace.append("trend_escalation: medium urgency actions promoted to high")

        # 3. Localised infection — targeted physical removal first
        if fm.get("infection_spread") == "localised":
            actions.insert(0, {
                "action"  : "Targeted removal of the infected region — infection is still localised",
                "category": "physical", "urgency": "high", "priority": 9.2,
            })
            adaptations.append({"type": "localised_boost", "detail": "targeted_removal_added"})
            trace.append("localised_boost: targeted removal prepended")

        # 4. Isolation mandate from inference engine
        if "True" in inf_map.get("must_isolate", []):
            actions.insert(0, {
                "action"  : "Immediately isolate infected plants from the rest of the crop",
                "category": "containment", "urgency": "critical", "priority": 10.8,
            })
            adaptations.append({"type": "isolation_mandate", "detail": "must_isolate=True"})
            trace.append("isolation_mandate: must_isolate rule fired")

        # 5. Environmental actions from inference
        for env_act in inf_map.get("environmental_action", []):
            actions.append({
                "action"  : f"Environmental control: {env_act.replace('_', ' ')}",
                "category": "environmental", "urgency": "medium", "priority": 5.5,
            })
            trace.append(f"env_action: {env_act}")

        # 6. Preventive treatment for neighbours
        if "neighbouring_plants" in inf_map.get("preventive_treatment", []):
            actions.append({
                "action"  : "Apply preventive treatment to all neighbouring plants within 24 hours",
                "category": "containment", "urgency": "high", "priority": 8.8,
            })
            trace.append("preventive_treatment: critical spread risk triggered")

        # 7. Monitoring step (always last)
        freq = inf_map.get("monitoring_frequency", ["every_5_days"])[0]
        actions.append({
            "action"  : f"Re-inspection: {freq.replace('_', ' ')}",
            "category": "monitoring", "urgency": "low", "priority": 2.0,
        })

        actions.sort(key=lambda a: -a["priority"])
        for i, a in enumerate(actions, start=1):
            a["step"] = i

        escalation = (
            trend.get("severity_trend") == "increasing"
            or trend.get("spread_trend") == "spreading"
        )
        overall_urgency = actions[0]["urgency"] if actions else "low"

        if confidence >= 0.85:
            conf_note = f"High confidence ({confidence:.1%}) — plan is reliable."
        elif confidence >= 0.60:
            conf_note = f"Moderate confidence ({confidence:.1%}) — verify diagnosis if possible."
        else:
            conf_note = f"Low confidence ({confidence:.1%}) — expert verification included as Step 1."

        return TreatmentPlan(
            disease_type        = fm.get("disease_type_is", "Unknown"),
            actions             = actions,
            adaptations         = adaptations,
            inference_trace     = trace,
            monitoring_interval = trend.get("summary", "Re-inspect in 5 days."),
            escalation_flag     = escalation,
            confidence_note     = conf_note,
            overall_urgency     = overall_urgency,
        )
