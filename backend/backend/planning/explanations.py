"""
backend/planning/explanations.py
─────────────────────────────────
Human-Adaptive Explanation Generator for ExplainPlan-Vision.

Fixes applied vs. original:
  1. Removed all === / ──── separator lines from output strings
  2. Farmer explanation now reads as natural spoken language, not a CLI printout
  3. Agronomist explanation drops raw inference dumps; uses prose with embedded values
  4. Researcher explanation restructured as a readable report, not a console log
  5. Counterfactual urgency "unknown→unknown" fixed — urgency is now derived from
     reasoning output and passed through correctly
  6. Temporal trend "Insufficient observation history" replaced with a meaningful
     first-observation message
  7. Severity label "high" now displayed as "High" (capitalised) throughout
  8. Confidence shown as percentage (87.6%) not raw float (0.8758) in farmer view
  9. Disease name "Tomato_Early_blight" → "Early Blight on Tomato" in farmer view
 10. Phase 1 notebook markdown cells humanised (separate file: phase1_fixes.md)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


# ── Data contract ─────────────────────────────────────────────────────────────

@dataclass
class PredictionResult:
    disease: str          # e.g. "Tomato___Early_blight"
    plant: str            # e.g. "Tomato"
    disease_type: str     # e.g. "Early blight"
    confidence: float     # 0–1
    severity: str         # "high" | "medium" | "low"
    is_healthy: bool

@dataclass
class XAIResult:
    infection_spread: str   # "localised" | "moderate" | "widespread"
    focus_score: float
    activation_entropy: float

@dataclass
class ReasoningResult:
    urgency_level: str        # "critical" | "high" | "medium" | "low"
    urgency_score: float
    spread_risk: str
    treatment_class: str
    requires_isolation: bool
    escalation_flag: bool
    rules_fired: int
    confused_with: Optional[str] = None

@dataclass
class PlanAction:
    step: int
    action: str
    priority: str   # "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"

@dataclass
class PlanResult:
    actions: list[PlanAction]
    monitoring_interval: str   # e.g. "every 5 days"
    escalation_flag: bool
    confidence_note: str
    adaptations: list[str]

@dataclass
class CounterfactualScenario:
    key: str
    description: str
    original_actions: int
    cf_actions: int
    delta: int
    original_urgency: str
    cf_urgency: str
    narrative: str

@dataclass
class TrendResult:
    available: bool
    severity_trend: Optional[str] = None    # "improving" | "stable" | "worsening"
    urgency_trend: Optional[str] = None
    n_observations: int = 1
    summary: Optional[str] = None


# ── Helper ────────────────────────────────────────────────────────────────────

def _clean_disease_name(raw: str) -> str:
    """
    Convert raw PlantVillage label to a readable disease name.
    'Tomato___Early_blight'  →  'Early Blight'
    'Pepper__bell___healthy' →  'Healthy'
    """
    if "___" in raw:
        disease_part = raw.split("___", 1)[1]
    else:
        parts = raw.split("_")
        disease_part = " ".join(parts[1:]) if len(parts) > 1 else raw

    return disease_part.replace("_", " ").strip().title()


def _severity_word(severity: str) -> str:
    """Maps 'high'/'medium'/'low' to a natural English severity phrase."""
    return {
        "high":   "serious",
        "medium": "moderate",
        "low":    "mild",
    }.get(severity.lower(), severity)


def _urgency_phrase(urgency: str) -> str:
    return {
        "critical": "requires immediate action today",
        "high":     "should be treated within the next 24–48 hours",
        "medium":   "should be addressed this week",
        "low":      "can be monitored and treated at your next scheduled visit",
    }.get(urgency.lower(), "should be assessed by an agronomist")


def _spread_phrase(spread: str) -> str:
    return {
        "widespread":  "has already spread across a large area of the leaf surface",
        "moderate":    "has spread to a moderate portion of the leaf",
        "localised":   "is currently contained to a small area of the leaf",
    }.get(spread.lower(), spread)


def _trend_sentence(trend: TrendResult) -> str:
    if not trend.available:
        return (
            "This is the first time this plant has been analysed. "
            "Run another scan in a few days to start tracking whether the disease is improving or getting worse."
        )
    if trend.severity_trend == "worsening":
        return (
            f"Compared to your last {trend.n_observations} scans, the disease appears to be getting worse. "
            "It is important to act quickly."
        )
    if trend.severity_trend == "improving":
        return (
            f"Good news — compared to your last {trend.n_observations} scans, the disease appears to be improving. "
            "Keep following the treatment plan."
        )
    return (
        f"The disease has remained stable over your last {trend.n_observations} scans. "
        "Continue the current treatment and monitor closely."
    )


# ── Bug fix: counterfactual urgency ──────────────────────────────────────────
# Original bug: urgency was printed as "unknown→unknown" because the
# CounterfactualScenario object was built without looking up urgency from the
# reasoning engine. Fix: urgency is now passed in from the caller.

def _cf_urgency_sentence(scenario: CounterfactualScenario) -> str:
    """Describe what would change under this counterfactual."""
    delta_word = "fewer" if scenario.delta < 0 else ("more" if scenario.delta > 0 else "the same number of")
    delta_abs = abs(scenario.delta)

    urgency_change = ""
    if scenario.original_urgency and scenario.cf_urgency:
        if scenario.original_urgency != scenario.cf_urgency:
            urgency_change = (
                f" Urgency would drop from **{scenario.original_urgency}** "
                f"to **{scenario.cf_urgency}**."
            )

    if scenario.delta == 0:
        return (
            f"Under this scenario the plan would remain the same length ({scenario.cf_actions} steps).{urgency_change} "
            f"{scenario.narrative}"
        )

    return (
        f"Under this scenario the plan would need {delta_abs} {delta_word} steps "
        f"({scenario.original_actions} → {scenario.cf_actions}).{urgency_change} "
        f"{scenario.narrative}"
    )


# ── Farmer explanation ────────────────────────────────────────────────────────

def format_farmer_explanation(
    prediction: PredictionResult,
    xai: XAIResult,
    reasoning: ReasoningResult,
    plan: PlanResult,
    trend: TrendResult,
) -> str:
    """
    Plain-language explanation for a farmer with no technical background.
    No raw numbers, no separator lines, no CLI formatting.
    """
    disease_name   = _clean_disease_name(prediction.disease)
    severity_word  = _severity_word(prediction.severity)
    spread_desc    = _spread_phrase(xai.infection_spread)
    urgency_phrase = _urgency_phrase(reasoning.urgency_level)
    confidence_pct = f"{prediction.confidence * 100:.0f}%"
    trend_sentence = _trend_sentence(trend)

    isolation_note = ""
    if reasoning.requires_isolation:
        isolation_note = (
            "\n\nImportantly, this disease can spread to nearby plants. "
            "Keep the affected plant away from healthy ones until treated."
        )

    steps_text = ""
    for action in plan.actions:
        steps_text += f"\n  {action.step}. {action.action}"

    monitoring = f"Check the plant again {plan.monitoring_interval}."

    return (
        f"Your {prediction.plant} plant has been diagnosed with {disease_name}. "
        f"The AI is {confidence_pct} confident in this diagnosis.\n\n"
        f"This is a {severity_word} problem. The infection {spread_desc}, "
        f"so it {urgency_phrase}."
        f"{isolation_note}\n\n"
        f"Here is what to do:\n"
        f"{steps_text}\n\n"
        f"{monitoring}\n\n"
        f"{trend_sentence}"
    )


# ── Agronomist explanation ────────────────────────────────────────────────────

def format_agronomist_explanation(
    prediction: PredictionResult,
    xai: XAIResult,
    reasoning: ReasoningResult,
    plan: PlanResult,
    counterfactuals: list[CounterfactualScenario],
    trend: TrendResult,
) -> str:
    """
    Technical explanation for an agronomist. Uses domain vocabulary,
    includes key inferences, counterfactual summary, and monitoring protocol.
    No separator lines. No raw confidence floats in the header.
    """
    disease_name  = _clean_disease_name(prediction.disease)
    conf_pct      = f"{prediction.confidence * 100:.1f}%"
    spread        = xai.infection_spread.capitalize()
    urgency       = reasoning.urgency_level.capitalize()
    treatment_cls = reasoning.treatment_class.replace("_", " ").title()

    # Build key inference summary as natural prose
    inference_notes = []
    if reasoning.requires_isolation:
        inference_notes.append("plant isolation is indicated due to widespread severity")
    if reasoning.treatment_class:
        inference_notes.append(f"primary treatment class is {reasoning.treatment_class.replace('_', ' ')}")
    if reasoning.confused_with:
        inference_notes.append(
            f"differential diagnosis note: consider {reasoning.confused_with.replace('_', ' ')} "
            f"if symptoms develop water-soaked margins"
        )
    inference_text = "; ".join(inference_notes).capitalize() + "." if inference_notes else ""

    # Treatment steps as a numbered list
    steps_lines = []
    for a in plan.actions:
        steps_lines.append(f"  [{a.priority:8s}] {a.step}. {a.action}")
    steps_text = "\n".join(steps_lines)

    # Counterfactual summary — now with real urgency values
    cf_lines = []
    for cf in counterfactuals:
        cf_lines.append(
            f"  {cf.description}: {_cf_urgency_sentence(cf)}"
        )
    cf_text = "\n\n".join(cf_lines)

    # Trend
    trend_text = _trend_sentence(trend)

    escalation = "Escalation to a specialist is recommended." if plan.escalation_flag else ""

    return (
        f"Crop: {prediction.plant}\n"
        f"Diagnosis: {disease_name} ({conf_pct} confidence)\n"
        f"Pathogen class: {prediction.disease_type.title()}\n"
        f"Severity: {prediction.severity.capitalize()} | Spread: {spread} | "
        f"Spread risk: {reasoning.spread_risk.capitalize()}\n"
        f"Urgency level: {urgency} | Treatment class: {treatment_cls}\n"
        f"Inference rules fired: {reasoning.rules_fired}\n\n"
        f"{inference_text}\n\n"
        f"Treatment sequence ({len(plan.actions)} steps):\n"
        f"{steps_text}\n\n"
        f"Monitoring protocol: {plan.monitoring_interval}\n"
        f"Plan reliability: {plan.confidence_note}\n"
        f"{escalation}\n\n"
        f"Counterfactual analysis:\n{cf_text}\n\n"
        f"Temporal status: {trend_text}"
    ).strip()


# ── Researcher explanation ────────────────────────────────────────────────────

def format_researcher_explanation(
    prediction: PredictionResult,
    xai: XAIResult,
    reasoning: ReasoningResult,
    plan: PlanResult,
    counterfactuals: list[CounterfactualScenario],
    symbolic_facts: list[dict],
    inferences: list[dict],
    trend: TrendResult,
) -> str:
    """
    Full technical trace for a researcher. Includes all symbolic facts,
    inference outputs with confidence scores, counterfactual analysis,
    and temporal trend. Structured as a readable research report,
    not a console dump.
    """
    disease_name = _clean_disease_name(prediction.disease)
    conf_pct     = f"{prediction.confidence * 100:.2f}%"

    # Symbolic facts table
    facts_lines = []
    for f in symbolic_facts:
        pred = f.get("predicate", "")
        args = ", ".join(str(a) for a in f.get("arguments", []))
        conf = f.get("confidence", 0)
        src  = f.get("source", "")
        facts_lines.append(f"  {pred}({args})  [conf={conf:.3f}, src={src}]")
    facts_text = "\n".join(facts_lines) if facts_lines else "  (none)"

    # Inference outputs
    inf_lines = []
    for inf in inferences:
        conclusion = inf.get("conclusion", inf.get("predicate", str(inf)))
        conf       = inf.get("confidence", inf.get("score", ""))
        rule       = inf.get("rule", inf.get("via", ""))
        conf_str   = f"[{conf:.3f}]" if isinstance(conf, float) else ""
        rule_str   = f"via {rule}" if rule else ""
        inf_lines.append(f"  {conclusion} {conf_str} {rule_str}".strip())
    inf_text = "\n".join(inf_lines) if inf_lines else "  (none)"

    # Plan
    plan_lines = []
    for a in plan.actions:
        plan_lines.append(f"  [{a.step:02d}] [{a.priority:8s}] {a.action}")
    plan_text = "\n".join(plan_lines)

    # Counterfactuals — full detail
    cf_lines = []
    for cf in counterfactuals:
        orig_urg = cf.original_urgency or "n/a"
        cf_urg   = cf.cf_urgency or "n/a"
        cf_lines.append(
            f"  [{cf.key}]\n"
            f"    Scenario:  {cf.description}\n"
            f"    Actions:   {cf.original_actions} → {cf.cf_actions} (delta={cf.delta:+d})\n"
            f"    Urgency:   {orig_urg} → {cf_urg}\n"
            f"    Narrative: {cf.narrative}"
        )
    cf_text = "\n\n".join(cf_lines) if cf_lines else "  (none)"

    # Trend
    trend_text = _trend_sentence(trend)

    return (
        f"ExplainPlan-Vision — Neuro-Symbolic Analysis Report\n\n"

        f"Vision Module\n"
        f"  Model      : EfficientNet-B0\n"
        f"  Prediction : {disease_name}\n"
        f"  Confidence : {conf_pct}\n"
        f"  Severity   : {prediction.severity.capitalize()}\n"
        f"  Plant      : {prediction.plant}\n\n"

        f"XAI Module (Grad-CAM++)\n"
        f"  Focus score       : {xai.focus_score:.4f}\n"
        f"  Infection spread  : {xai.infection_spread.capitalize()}\n"
        f"  Activation entropy: {xai.activation_entropy:.4f}\n\n"

        f"Symbolic Fact Extraction ({len(symbolic_facts)} facts)\n"
        f"{facts_text}\n\n"

        f"Inference Engine Output ({reasoning.rules_fired} rules fired)\n"
        f"{inf_text}\n\n"

        f"Dynamic Plan ({len(plan.actions)} actions)\n"
        f"  Confidence note: {plan.confidence_note}\n"
        f"  Escalation flag: {plan.escalation_flag}\n"
        f"  Adaptations    : {'; '.join(plan.adaptations) if plan.adaptations else 'none'}\n"
        f"{plan_text}\n\n"

        f"Counterfactual Analysis\n"
        f"{cf_text}\n\n"

        f"Temporal Trend\n"
        f"  {trend_text}"
    )
