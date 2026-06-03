"""
Generates four counterfactual scenarios by modifying one variable at a time,
re-running inference, and computing the delta in plan length and urgency.
"""

from __future__ import annotations
from dataclasses import replace
from typing import Dict, List

from backend.reasoning.facts import SymbolicFact
from backend.reasoning.engine import InferenceFact, NSReasoningEngine
from backend.planning.engine import ContextEngine, TreatmentPlan

_NEUTRAL = {
    "severity_trend": "stable", "spread_trend": "stable",
    "summary": "Counterfactual scenario",
    "latest_urgency": "medium", "latest_severity": "medium",
}


def _modify(facts: List[SymbolicFact], predicate: str, value: str) -> List[SymbolicFact]:
    return [replace(f, arguments=[value]) if f.predicate == predicate else f for f in facts]


def _urgency(inferences: List[InferenceFact]) -> str:
    return next((i.arguments[0] for i in inferences if i.predicate == "urgency_level"), "unknown")


def generate_counterfactuals(
    facts      : List[SymbolicFact],
    inferences : List[InferenceFact],
    plan       : TreatmentPlan,
    prediction : Dict,
) -> List[Dict]:
    """Return four counterfactual dicts."""
    reasoner = NSReasoningEngine.get()
    planner  = ContextEngine.get()
    orig_n   = len(plan.actions)
    dt       = prediction["disease_type"]
    cfs: List[Dict] = []

    # 1. Lower severity
    ladder  = ["low", "medium", "high"]
    cur_idx = ladder.index(prediction["severity"]) if prediction["severity"] in ladder else 2
    if cur_idx > 0:
        lower = ladder[cur_idx - 1]
        f1    = _modify(facts, "severity_is", lower)
        i1    = reasoner.reason(f1, dt)
        p1    = planner.generate_plan(f1, i1, _NEUTRAL)
        cfs.append({
            "scenario": "lower_severity",
            "description": f"If severity were {lower} instead of {prediction['severity']}",
            "plan_delta": len(p1.actions) - orig_n,
            "original_actions": orig_n,
            "cf_actions": len(p1.actions),
            "original_urgency": _urgency(inferences),
            "cf_urgency": _urgency(i1),
            "narrative": (
                f"Reducing severity from {prediction['severity']} to {lower} would change "
                f"the plan from {orig_n} to {len(p1.actions)} actions. "
                f"Early intervention preventing escalation is the highest-value control measure."
            ),
        })

    # 2. Earlier detection (localised spread)
    f2 = _modify(facts, "infection_spread", "localised")
    f2 = _modify(f2, "requires_isolation", "False")
    i2 = reasoner.reason(f2, dt)
    p2 = planner.generate_plan(f2, i2, {**_NEUTRAL, "spread_trend": "contained"})
    cfs.append({
        "scenario": "earlier_detection",
        "description": "If the disease had been detected while still localised",
        "plan_delta": len(p2.actions) - orig_n,
        "original_actions": orig_n,
        "cf_actions": len(p2.actions),
        "original_urgency": _urgency(inferences),
        "cf_urgency": _urgency(i2),
        "narrative": (
            f"Early detection with localised spread reduces the plan from {orig_n} to "
            f"{len(p2.actions)} actions. Targeted physical removal suffices; "
            f"chemical load and isolation requirements both decrease. "
            f"This quantifies the return on weekly monitoring investment."
        ),
    })

    # 3. Borderline confidence (65%)
    f3 = [replace(f, confidence=0.65) for f in facts]
    f3 = _modify(f3, "confidence_level", "moderate")
    i3 = reasoner.reason(f3, dt)
    p3 = planner.generate_plan(f3, i3, _NEUTRAL)
    cfs.append({
        "scenario": "lower_confidence",
        "description": "If model confidence were 65% (borderline reliability threshold)",
        "plan_delta": len(p3.actions) - orig_n,
        "original_actions": orig_n,
        "cf_actions": len(p3.actions),
        "original_urgency": _urgency(inferences),
        "cf_urgency": _urgency(i3),
        "narrative": (
            f"At 65% confidence a verification step is prepended before any chemical treatment. "
            f"The plan changes from {orig_n} to {len(p3.actions)} actions. "
            f"Lower confidence triggers conservative planning rather than the same aggressive treatment."
        ),
    })

    # 4. Optimal environment (non-favouring conditions)
    f4   = [f for f in facts if not f.predicate.startswith("favoured_by")]
    stub = replace(facts[0], predicate="favoured_by_humidity", arguments=["low"], source="counterfactual")
    f4.append(stub)
    i4 = reasoner.reason(f4, dt)
    p4 = planner.generate_plan(f4, i4, {**_NEUTRAL, "severity_trend": "decreasing", "spread_trend": "contained"})
    cfs.append({
        "scenario": "optimal_environment",
        "description": "If environmental conditions were not favouring the pathogen",
        "plan_delta": len(p4.actions) - orig_n,
        "original_actions": orig_n,
        "cf_actions": len(p4.actions),
        "original_urgency": _urgency(inferences),
        "cf_urgency": _urgency(i4),
        "narrative": (
            f"Under non-favouring conditions (low humidity, no leaf wetness) environmental "
            f"control actions reduce. Chemical steps remain because {dt} requires treatment "
            f"regardless of environment. Environmental management reduces total treatment burden."
        ),
    })

    return cfs
