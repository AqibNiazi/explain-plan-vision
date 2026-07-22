# Phase 3 & 4 — Planning and Neuro-Symbolic Reasoning: Findings

---

## Phase 3 — Adaptive Planning Engine

### Design Goals

1. Treatment steps must be *grounded* — derived from the reasoning trace, not from a fixed template per disease class.
2. Steps must be *ordered by urgency* — a critical-urgency fungal disease should isolate first, treat second, monitor third.
3. The plan must *adapt* to context — the same disease in a widespread vs. localised state requires meaningfully different actions.

### The 6 Context Mechanisms

| Mechanism | How It Adapts the Plan |
|---|---|
| Disease type (fungal/bacterial/viral) | Sets treatment_class: fungicide / copper bactericide / cultural removal |
| Infection spread (localised/moderate/widespread) | Adds/removes isolation and containment steps |
| Urgency score (0–1 continuous) | Sets monitoring_interval: daily / weekly / bi-weekly |
| Seasonal modifier | Adjusts chemical application frequency (wet season → increase) |
| Severity level (low/medium/high) | Scales the number of treatment steps |
| Temporal trend (improving/stable/worsening) | Escalates plan if worsening detected |

### Counterfactual Analysis

Four scenarios are computed for every analysis, each producing an independent plan:

| Scenario | Manipulation | Purpose |
|---|---|---|
| `early_detection` | confidence +0.10, severity → medium | How much simpler would the plan be with earlier detection? |
| `isolated_spread` | spread → localised | How much does spread pattern change the plan? |
| `critical_severity` | severity → high, urgency_score +0.15 | What does worst-case look like? |
| `healthy_baseline` | disease → healthy | Counterfactual null (what if the plant were fine?) |

**Key finding from counterfactual analysis:** For Late Blight at widespread spread, the `early_detection` scenario reduces the plan from 8 steps to 4 steps (plan_delta = -4) and drops urgency from critical → medium. This quantitative delta is a meaningful research result: it establishes the *value of early detection* in concrete action-count terms.

### Decision Tree Look-ahead

A probabilistic decision tree is constructed from the plan actions, estimating state transitions at each branch. The `expected_urgency` scalar is computed via leaf-weighted averaging.

**Observation:** expected_urgency consistently underestimates worst-case urgency by 0.08–0.14 units due to optimistic branching assumptions. This is a known limitation documented in the API response as `confidence_note`.

---

## Phase 4 — Neuro-Symbolic Reasoning

### The Grounding Pipeline

The core architectural decision of Phase 4 is the *grounding step*: the explicit conversion of continuous neural outputs into discrete, verifiable symbolic facts before any inference is performed.

```
Neural output: confidence=0.97, severity_score=0.82, spread_fraction=0.63
                          ↓ grounding function
Symbolic fact: confidence_level(high, 0.97)
Symbolic fact: severity_level(high, 0.85)
Symbolic fact: infection_spread(widespread, 0.91)
```

This step is what makes the reasoning auditable. A clinician or agronomist can inspect the symbolic facts and verify whether each is consistent with what they observe in the image — without understanding the neural network at all.

### Knowledge Graph Construction

The disease knowledge graph was constructed with NetworkX, encoding:

- **Nodes:** disease classes, disease types, treatment classes, severity levels, urgency levels
- **Edges:** causal relationships, treatment compatibilities, spread risk associations
- **Weights:** prior probabilities from plant pathology literature

### Inference Rule Categories

| Category | Count | Example |
|---|---|---|
| Disease-type rules | 4 | `fungal_disease → treatment_class(fungicide)` |
| Severity escalation rules | 5 | `severity(high) ∧ spread(widespread) → urgency(critical)` |
| Isolation rules | 3 | `spread(widespread) → requires_isolation(true)` |
| Seasonal adjustment rules | 3 | `season(wet) ∧ fungal → increase_treatment_frequency` |
| Temporal trend rules | 3 | `trend(worsening) → escalation_flag(true)` |
| Composite urgency rules | 3 | `urgency_score = f(confidence, severity, spread)` |

### Key Finding — Rules Fired vs. Urgency Correlation

Across 150 test analyses, the number of rules fired showed strong positive correlation with urgency_score (r = 0.81). This is expected: more rules fire when more risk factors are simultaneously present. It validates that the rule set is internally consistent.

### Key Finding — Reasoning Tracability

Every symbolic fact carries:
- `predicate` — the proposition being asserted
- `arguments` — entities it applies to
- `confidence` — propagated from neural output
- `source` — `vision`, `xai`, or `derived`

This trace structure means every treatment recommendation in the plan can be walked back to the neural confidence value that produced the symbolic fact that triggered the inference rule that generated it. This end-to-end traceability is the primary research contribution.

### Limitations

1. **Closed-world assumption.** The KG contains a fixed set of diseases. An unseen disease class produces degraded reasoning quality.
2. **Rule confidence propagation is heuristic.** Confidence values are multiplied through rule chains, which is a simplification of proper probabilistic inference.
3. **Seasonal modifier is static.** Currently set at deployment time; a real system would use geolocation + date to infer season automatically.

---

## Phase 5 — Deployment Notes

See `docs/architecture/system_overview.md` for full deployment diagram.

**Key deployment decisions:**

- Singleton orchestrator pattern — all engines initialised once at startup, not per request. Reduces per-request latency from ~8s → ~2.1s.
- `register_full_backward_hook` throughout XAI — avoids deprecated hook warnings in PyTorch 2.2.
- numpy pinned to `1.26.4` — prevents ABI incompatibility with torch 2.2+cpu wheel.
- torch CPU-only wheel explicitly installed before all other packages — prevents pip from resolving CUDA wheel (~2.4GB).

---

## Future Work

1. **Phase 6 — LLM Grounding Layer.** Use a small LLM (Mistral-7B or GPT-4o API) to convert the symbolic reasoning trace into fluent natural language explanation. The LLM receives verified facts only — no raw image — preventing hallucination.

2. **Reasoning Alignment Evaluation.** Compare symbolic explanation vs. LLM-generated explanation on three metrics: factual consistency, hallucination rate, completeness. This evaluation could become a paper contribution.

3. **Probabilistic KG.** Replace deterministic rule thresholds with probabilistic inference (Markov Logic Networks or PSL) to propagate uncertainty more rigorously.

4. **Seasonal Geolocation.** Infer season from GPS + date rather than static configuration.
