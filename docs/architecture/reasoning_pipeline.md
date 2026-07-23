# Reasoning Pipeline ExplainPlan Vision

## Overview

The neuro-symbolic reasoning pipeline bridges neural perception (vision + XAI) and symbolic decision-making (planning + explanation) through a structured grounding step.

```
Neural Layer                    Symbolic Layer
────────────────                ────────────────────────────────────
EfficientNet-B0  ──────────► Symbolic Fact Extraction
Grad-CAM++       ──────────► (predicate + arguments + confidence)
                                         │
                                         ▼
                             Knowledge Graph Inference
                             (NetworkX · 20+ rules)
                                         │
                              ┌──────────┴──────────┐
                              ▼                     ▼
                        Derived Facts          Boolean Flags
                        urgency_score          requires_isolation
                        treatment_class        escalation_flag
                        spread_risk            disease_fungal
                              │
                    ┌─────────┴──────────┐
                    ▼                    ▼
              Adaptive Plan       Counterfactual
              Generator           Engine
```

## Stage 1 — Symbolic Fact Extraction

Neural outputs are converted into discrete, verifiable symbolic facts.
Each fact carries: predicate, arguments, confidence score, and source tag.

### Example Fact Set (Late Blight, confidence 0.97)

| Predicate | Arguments | Confidence | Source |
|---|---|---|---|
| `disease_detected` | `[tomato_late_blight]` | 0.974 | vision |
| `confidence_level` | `[high]` | 0.974 | vision |
| `severity_level` | `[high]` | 0.850 | vision |
| `infection_spread` | `[widespread]` | 0.910 | xai |
| `disease_type` | `[fungal]` | 1.000 | vision |
| `focus_score` | `[0.723]` | 0.910 | xai |
| `activation_entropy` | `[1.241]` | 0.910 | xai |
| `host_plant` | `[tomato]` | 1.000 | vision |
| `is_healthy` | `[false]` | 0.974 | vision |

Confidence thresholds for discretisation:
- `confidence_level`: high ≥ 0.85 / medium ≥ 0.65 / low < 0.65
- `severity_level`: high ≥ 0.75 / medium ≥ 0.45 / low < 0.45
- `infection_spread`: direct from GradCAM spatial statistics

## Stage 2 — Knowledge Graph

Built with NetworkX at startup, held in memory for zero per-request init cost.

| Property | Value |
|---|---|
| Nodes | 48 |
| Edges | 112 |
| Disease class nodes | 15 |
| Inference rules | 20+ |

Node types: DiseaseClass, DiseaseType, TreatmentClass, SeverityLevel, UrgencyLevel, SpreadPattern

## Stage 3 — Inference Rules (Selected)

**Disease Type Rules**
```
disease_type(fungal) → treatment_class(fungicide)  [conf: 1.0]
disease_type(bacterial) → treatment_class(bactericide)  [conf: 1.0]
```

**Severity Escalation Rules**
```
severity(high) ∧ spread(widespread) → urgency(critical)  [conf: 0.95]
severity(high) ∧ spread(moderate) → urgency(high)  [conf: 0.90]
severity(medium) ∧ spread(widespread) → urgency(high)  [conf: 0.85]
```

**Isolation Rules**
```
spread(widespread) → requires_isolation(true)  [conf: 0.95]
disease_type(fungal) ∧ spread(moderate) → requires_isolation(true)  [conf: 0.70]
```

**Composite Urgency Score**
```
urgency_score = 0.30*confidence + 0.35*severity_numeric
              + 0.25*spread_numeric + 0.10*focus_score
```

**Temporal Trend Rules**
```
trend(worsening) → escalation_flag(true) ∧ monitoring(daily)
trend(improving) → monitoring(bi-weekly)
```

## Stage 4 — Confidence Propagation

Multiplicative model through inference chains:
```
derived_confidence = product(antecedent_confidences) × rule_reliability

Example:
  severity(high): 0.850 × spread(widespread): 0.910 × rule: 0.95
  → urgency(critical): 0.734
```

**Known limitation:** Multiplicative propagation underestimates confidence when antecedents are correlated. A Bayesian network would handle this correctly and is a planned Phase 7 improvement.

## Reasoning Trace — API Response Shape

```json
{
  "symbolic_facts": [{"predicate": "...", "arguments": [...], "confidence": 0.0, "source": "vision|xai"}],
  "inferences": ["urgency_level(critical)", "treatment_class(fungicide)", "..."],
  "urgency_level": "critical",
  "urgency_score": 0.87,
  "spread_risk": "high",
  "treatment_class": "fungicide",
  "requires_isolation": true,
  "escalation_flag": true,
  "rules_fired": 14
}
```

Every field traces back to a specific rule or grounding function full auditability without inspecting the neural network.
