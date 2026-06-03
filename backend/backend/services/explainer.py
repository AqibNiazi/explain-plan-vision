"""
Renders the same reasoning trace in three expertise modes.
Farmer, agronomist, and researcher modes differ in vocabulary,
structure, and the level of technical detail shown.
"""

from __future__ import annotations
from typing import Dict, List

from backend.reasoning.facts import SymbolicFact
from backend.reasoning.engine import InferenceFact
from backend.planning.engine import TreatmentPlan


class NSExplainer:
    _instance: NSExplainer | None = None

    @classmethod
    def get(cls) -> NSExplainer:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def render_all(
        self,
        prediction      : Dict,
        facts           : List[SymbolicFact],
        inferences      : List[InferenceFact],
        plan            : TreatmentPlan,
        counterfactuals : List[Dict],
        trend           : Dict,
    ) -> Dict[str, str]:
        return {
            "farmer"     : self._farmer(prediction, plan, trend),
            "agronomist" : self._agronomist(prediction, facts, inferences, plan, trend),
            "researcher" : self._researcher(prediction, facts, inferences, plan, counterfactuals, trend),
        }

    def _farmer(self, pred: Dict, plan: TreatmentPlan, trend: Dict) -> str:
        lines = ["PLANT HEALTH REPORT", "=" * 40]
        if pred["is_healthy"]:
            lines += [
                f"Your {pred['plant']} plant looks healthy.",
                "Keep up regular weekly monitoring.",
            ]
        else:
            urgency_msg = {
                "immediate": "ACT TODAY — this is very serious.",
                "high"     : "Act within the next 2 days.",
                "medium"   : "Act this week.",
                "low"      : "Low urgency — act when convenient.",
            }
            lines += [
                f"Problem found: {pred['disease_type']} on your {pred['plant']}.",
                f"Seriousness: {pred['severity'].upper()}",
                urgency_msg.get(plan.overall_urgency, "Take action soon."),
                "",
                "What to do:",
            ]
            for a in plan.actions[:6]:
                if a.get("category") != "monitoring":
                    lines.append(f"  Step {a['step']}: {a['action']}")
            if plan.escalation_flag:
                lines += [
                    "",
                    "WARNING: The situation is getting worse.",
                    "Act immediately and re-check in 24 hours.",
                ]
            lines += ["", f"Re-check the plant: {plan.monitoring_interval.split('.')[0]}."]
        return "\n".join(lines)

    def _agronomist(
        self,
        pred       : Dict,
        facts      : List[SymbolicFact],
        inferences : List[InferenceFact],
        plan       : TreatmentPlan,
        trend      : Dict,
    ) -> str:
        fm   = {f.predicate: f.arguments[0] for f in facts}
        skip = {"urgency_score", "focus_score", "activation_entropy", "embedding_norm"}
        lines = [
            "AGRONOMIC TREATMENT PLAN", "=" * 55,
            f"Crop           : {pred['plant']}",
            f"Diagnosis      : {pred['disease_type']}",
            f"Pathogen type  : {fm.get('pathogen_type_is', '?')}",
            f"Confidence     : {pred['confidence']:.4f}",
            f"Severity       : {pred['severity']}",
            f"Spread pattern : {fm.get('infection_spread', '?')}",
            f"Spread risk    : {fm.get('spread_risk', '?')}",
            f"Treatment class: {fm.get('treatment_class', '?')}",
            "",
            "Key inferences fired:",
        ]
        shown = set()
        for inf in inferences:
            if inf.predicate in shown or inf.predicate in skip:
                continue
            lines.append(f"  {inf.predicate}: {', '.join(inf.arguments)} (rule: {inf.rule_fired})")
            shown.add(inf.predicate)
        lines += ["", "Treatment sequence:"]
        for a in plan.actions:
            lines.append(f"  [{a['urgency'].upper():8s}] {a['step']}. {a['action']}")
        lines += [
            "",
            f"Monitoring : {plan.monitoring_interval}",
            f"Escalation : {'YES — increase monitoring' if plan.escalation_flag else 'No'}",
            f"Trend      : {trend.get('summary', 'Insufficient data')}",
        ]
        return "\n".join(lines)

    def _researcher(
        self,
        pred            : Dict,
        facts           : List[SymbolicFact],
        inferences      : List[InferenceFact],
        plan            : TreatmentPlan,
        counterfactuals : List[Dict],
        trend           : Dict,
    ) -> str:
        fm    = {f.predicate: f.arguments[0] for f in facts}
        lines = [
            "ExplainPlan-Vision — Neuro-Symbolic Reasoning Report",
            "=" * 65,
            "VISION MODULE",
            f"  Model       : EfficientNet-B0 (Phase 1 checkpoint)",
            f"  Disease     : {pred['disease']}",
            f"  Confidence  : {pred['confidence']:.4f}",
            f"  Severity    : {pred['severity']}",
            f"  Runner-up   : {pred['top3'][1]['disease_class']} ({pred['top3'][1]['confidence']:.4f})"
              if len(pred["top3"]) > 1 else "",
            "",
            "XAI MODULE (Grad-CAM++)",
            f"  Focus score       : {fm.get('focus_score', 'N/A')}",
            f"  Infection spread  : {fm.get('infection_spread', 'N/A')}",
            f"  Activation entropy: {fm.get('activation_entropy', 'N/A')}",
            "",
            "SYMBOLIC FACT EXTRACTION",
            f"  Total facts    : {len(facts)}",
            f"  Pathogen type  : {fm.get('pathogen_type_is', 'N/A')}",
            f"  Spread risk    : {fm.get('spread_risk', 'N/A')}",
            f"  Treatment class: {fm.get('treatment_class', 'N/A')}",
            f"  Requires iso   : {fm.get('requires_isolation', 'N/A')}",
            "",
            "INFERENCE ENGINE OUTPUT",
        ]
        for inf in inferences:
            lines.append(
                f"  {inf.predicate}({', '.join(inf.arguments)}) "
                f"[{inf.confidence:.3f}] via {inf.rule_fired}"
            )
        lines += [
            "",
            "DYNAMIC PLAN",
            f"  Actions     : {len(plan.actions)}",
            f"  Adaptations : {len(plan.adaptations)}",
            f"  Escalation  : {plan.escalation_flag}",
            f"  Confidence  : {plan.confidence_note}",
            "",
            "  Action sequence:",
        ]
        for a in plan.actions:
            lines.append(f"    [{a['step']:02d}] [{a['urgency'].upper():8s}] {a['action']}")
        lines += ["", "COUNTERFACTUAL ANALYSIS"]
        for cf in counterfactuals:
            lines.append(f"  {cf['scenario']}: {cf['description']}")
            lines.append(
                f"    {cf['original_actions']}→{cf['cf_actions']} actions "
                f"(delta={cf['plan_delta']:+d}), urgency: {cf['original_urgency']}→{cf['cf_urgency']}"
            )
            lines.append(f"    {cf['narrative'][:120]}...")
        lines += ["", "TEMPORAL TREND", f"  {trend.get('summary', 'No trend data.')}"]
        return "\n".join(lines)
