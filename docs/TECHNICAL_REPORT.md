# ExplainPlan Vision: An Explainable Neuro-Symbolic Visual Planning Agent for Plant Disease Diagnosis

**Technical Report TR-2026-01**  
Muhammad Aqib Niazi  
2026

---

## Abstract

We present **ExplainPlan Vision**, a full-stack neuro-symbolic system that diagnoses plant leaf disease from a single image and produces a complete, traceable explanation of every decision made — from pixel-level spatial attention to a prioritised, step-numbered treatment plan. The system integrates five AI paradigms in a sequential pipeline: deep visual classification (EfficientNet-B0), gradient-based spatial explanation (Grad-CAM++), first-order logic fact extraction, knowledge graph inference (NetworkX, 20+ rules), and a 6-context adaptive planning engine. A temporal memory component tracks disease progression across sessions and detects worsening trends. The system achieves **96.8% top-1 accuracy** on the PlantVillage benchmark (15 disease classes) and produces a complete 10-stage analysis in **~2.1 seconds on CPU**. The core contribution is the *grounding pipeline*: the explicit conversion of continuous neural outputs into verifiable symbolic facts before any planning decision is made, enabling full end-to-end traceability from pixel to treatment step. The system is deployed as a production web application with a FastAPI backend on HuggingFace Spaces and a React 19 frontend on Vercel.

**Keywords:** Explainable AI, Neuro-Symbolic AI, Plant Disease Diagnosis, Grad-CAM++, Knowledge Graph Reasoning, Adaptive Planning, EfficientNet

---

## 1. Introduction

Plant disease causes an estimated 20–40% of global crop yield loss annually (FAO, 2021). Early, accurate, and actionable diagnosis is critical — but it requires specialist agricultural knowledge that most smallholder farmers lack access to. Deep learning models have demonstrated strong performance on plant disease image classification, but two fundamental gaps persist in their practical deployment.

**Gap 1 — Explainability.** A model that outputs *"Tomato Late Blight, 97% confidence"* provides no information about *why* that conclusion was reached, *which regions* of the leaf were diagnostic, or how certain the model is about the spatial evidence. Without this transparency, farmers and agronomists cannot validate the output, and the system cannot be trusted in practice.

**Gap 2 — Planning.** Classification is not treatment. A farmer needs to know *what to do*, *how urgently*, *in what order*, and *what would happen if conditions were different*. A classifier that outputs a disease label and stops there has addressed only the diagnostic step of a much longer decision process.

ExplainPlan Vision addresses both gaps by combining: a vision backbone for classification, Grad-CAM++ for spatial explanation, a neuro-symbolic reasoning layer that derives urgency and treatment class from verifiable first-order logic facts, and an adaptive planning engine that produces a prioritised, annotated treatment plan with counterfactual analysis.

The system makes three specific contributions:

1. **The grounding pipeline.** A novel stage that explicitly converts continuous neural outputs and spatial statistics into first-order logic predicates with confidence scores. This makes every downstream reasoning step auditable without knowledge of the neural network.

2. **Spatial-to-symbolic mapping.** Grad-CAM++ spatial statistics (focus score, activation entropy, infection spread) are converted into symbolic facts that directly inform urgency and isolation decisions — creating a direct mechanistic link between spatial attention and treatment planning.

3. **End-to-end traceability.** Every treatment step in the final plan references the inference rule that triggered it, which references the symbolic fact that was asserted, which references the neural confidence value that produced it. This chain can be walked in either direction.

---

## 2. Related Work

### 2.1 Plant Disease Classification

Hughes and Salathé (2015) introduced the PlantVillage dataset, establishing the benchmark for leaf disease classification. Subsequent work demonstrated that CNNs can match or exceed expert agronomist accuracy on controlled benchmark images (Mohanty et al., 2016). EfficientNet (Tan & Le, 2019) improved the parameter-efficiency frontier, achieving comparable accuracy to ResNet50 with approximately 5× fewer parameters.

### 2.2 Explainable AI for Medical and Agricultural Imaging

Grad-CAM (Selvaraju et al., 2017) introduced gradient-weighted class activation mapping, producing spatial heatmaps that show which regions of an input image drove a classification decision. Grad-CAM++ (Chattopadhay et al., 2018) extended this with second-order gradient weighting, improving localisation precision for multi-instance images. LIME (Ribeiro et al., 2016) and SHAP (Lundberg & Lee, 2017) provide complementary perspectives — superpixel attribution and Shapley value attribution respectively — but at substantially higher computational cost.

### 2.3 Neuro-Symbolic AI

Neuro-symbolic systems combine the representational power of neural networks with the interpretability and formal reasoning capabilities of symbolic AI (Garcez et al., 2022). Relevant prior work includes neural theorem provers (Rocktäschel & Riedel, 2017) and differentiable logic programming (Evans & Grefenstette, 2018). Our approach differs in that we do not learn the symbolic rules — we hand-craft them from plant pathology domain knowledge and use neural outputs only as evidence.

### 2.4 AI Planning for Agricultural Decision Support

PDDL-based planning systems have been explored for crop management (Sabbadin et al., 2021), but these typically assume perfect state information. Our adaptive planner operates under uncertainty, using the confidence-weighted symbolic facts as a probabilistic state representation.

---

## 3. System Architecture

The system is organised into ten sequential processing stages, implemented as a singleton Orchestrator that coordinates four specialised engines.

### 3.1 Overview

```
Leaf Image (JPEG/PNG/WebP)
    │
    ├── Stage 01: EfficientNet-B0 Vision Engine
    │       → disease class, confidence, top-3, severity, is_healthy
    │
    ├── Stage 02: Grad-CAM++ XAI Engine  
    │       → heatmap_b64, focus_score, entropy, infection_spread
    │
    ├── Stage 03: Symbolic Fact Extraction
    │       → first-order logic predicates with confidence scores
    │
    ├── Stage 04: Knowledge Graph Inference
    │       → urgency_score, urgency_level, spread_risk, treatment_class
    │
    ├── Stage 05: Temporal Memory Update
    │       → severity_trend, urgency_trend, spread_trend
    │
    ├── Stage 06: Adaptive Plan Generation
    │       → numbered steps, 6 context mechanisms, escalation_flag
    │
    ├── Stage 07: Counterfactual Analysis
    │       → 4 scenarios, plan_delta per scenario, cf_urgency
    │
    ├── Stage 08: Decision Tree Look-ahead
    │       → expected_urgency scalar
    │
    ├── Stage 09: Human-Adaptive Explanations
    │       → farmer / agronomist / researcher narratives
    │
    └── Stage 10: Unified JSON Response
```

### 3.2 Vision Engine (Stage 01)

EfficientNet-B0 (Tan & Le, 2019) is used as the classification backbone, pre-trained on ImageNet and fine-tuned on PlantVillage. The classifier head is replaced: `Linear(1280, 15)`. The model is loaded once at startup into a singleton `VisionEngine` instance and is not reloaded between requests.

Severity is estimated from the confidence value and class metadata using a heuristic:

```
severity = high    if confidence > 0.85
severity = medium  if 0.65 ≤ confidence ≤ 0.85
severity = low     if confidence < 0.65
```

This heuristic is intentionally conservative — it is better to over-estimate severity than to recommend insufficient treatment.

### 3.3 XAI Engine (Stage 02)

Grad-CAM++ is applied to the final convolutional block of EfficientNet-B0. The implementation uses `register_full_backward_hook` (the deprecated `register_backward_hook` was removed in PyTorch 2.x). Hooks are always removed in `finally` blocks to prevent state leakage between concurrent requests.

Three spatial statistics are extracted from the normalised heatmap:

**Infection spread** — the fraction of heatmap pixels exceeding an activation threshold of 0.5, mapped to three discrete categories:
- localised: fraction < 0.20
- moderate: 0.20 ≤ fraction < 0.50
- widespread: fraction ≥ 0.50

**Focus score** — the ratio of peak to mean activation, measuring localisation sharpness:

$$\text{focus\_score} = \frac{\max(H)}{\text{mean}(H)}$$

**Activation entropy** — the Shannon entropy of the normalised heatmap distribution, measuring information concentration:

$$\text{entropy} = -\sum_{i} p_i \log_2(p_i)$$

where $p_i$ is the normalised activation value at pixel $i$.

### 3.4 Symbolic Grounding (Stage 03)

The grounding pipeline converts Stage 01 and Stage 02 outputs into first-order logic predicates. This is the central architectural decision of the system. Example output:

```
disease_detected(tomato_late_blight)  [confidence: 0.974, source: vision]
confidence_level(high)                [confidence: 0.974, source: vision]
severity_level(high)                  [confidence: 0.850, source: vision]
infection_spread(widespread)          [confidence: 0.910, source: xai]
disease_type(fungal)                  [confidence: 1.000, source: knowledge_base]
focus_score_high(0.723)               [confidence: 0.910, source: xai]
host_plant(tomato)                    [confidence: 1.000, source: knowledge_base]
```

Each fact carries:
- `predicate` — the proposition being asserted
- `arguments` — entities the proposition applies to
- `confidence` — propagated from the originating neural output
- `source` — `vision`, `xai`, or `knowledge_base`

The critical property of this representation is that an agronomist can inspect the symbolic facts and verify whether each is consistent with their own visual assessment of the leaf image — without accessing or understanding the neural network at all.

### 3.5 Knowledge Graph Inference (Stage 04)

The disease knowledge graph is constructed with NetworkX. It encodes disease classes, disease types, treatment classes, severity levels, and urgency levels as nodes, with causal relationships and treatment compatibilities as weighted edges.

Twenty-plus inference rules are organised into six categories:

| Category | Count | Example rule |
|---|---|---|
| Disease-type | 4 | `disease_type(fungal) → treatment_class(fungicide)` |
| Severity escalation | 5 | `severity(high) ∧ spread(widespread) → urgency(critical)` |
| Isolation | 3 | `spread(widespread) → requires_isolation(true)` |
| Seasonal adjustment | 3 | `season(wet) ∧ disease_type(fungal) → increase_treatment_frequency` |
| Temporal trend | 3 | `trend(worsening) → escalation_flag(true)` |
| Composite urgency | 3 | `urgency_score = f(confidence, severity, spread)` |

The composite urgency score is computed as a weighted combination of three symbolic facts:

$$\text{urgency\_score} = 0.4 \cdot \text{confidence} + 0.35 \cdot \text{severity\_weight} + 0.25 \cdot \text{spread\_weight}$$

where `severity_weight` and `spread_weight` are lookup values from the knowledge base.

### 3.6 Temporal Memory (Stage 05)

A sliding-window memory buffer stores the last N observations (default: 10). On each new analysis, the trend detection component compares the current observation against the window:

- `severity_trend` — improving if mean severity has decreased over the window, worsening if increased
- `urgency_trend` — same logic applied to urgency_score
- `spread_trend` — tracks infection_spread category transitions
- `disease_stable` — true if the same disease class has been detected in all window observations

The `monitoring_interval` recommendation adjusts based on detected trend: daily (worsening), weekly (stable), bi-weekly (improving).

### 3.7 Adaptive Planning Engine (Stage 06)

The planning engine generates a numbered treatment plan using six simultaneous context mechanisms:

| Mechanism | Effect on Plan |
|---|---|
| Disease type | Sets treatment class (fungicide / copper bactericide / cultural removal) |
| Infection spread | Adds/removes isolation and containment steps |
| Urgency score | Sets monitoring frequency and time constraints |
| Seasonal modifier | Adjusts chemical application interval |
| Severity level | Scales step count |
| Temporal trend | Escalates plan if worsening detected |

Each plan action carries a `category` (containment / chemical / physical / environmental / monitoring / verification) and an `urgency` annotation (critical / high / medium / low).

### 3.8 Counterfactual Analysis (Stage 07)

Four counterfactual scenarios are computed by manipulating symbolic facts and re-running the planning engine:

| Scenario | Manipulation | Research Purpose |
|---|---|---|
| `early_detection` | confidence +0.10, severity → medium | Quantifies value of early intervention |
| `isolated_spread` | spread → localised | Isolates spread pattern effect on plan complexity |
| `critical_severity` | severity → high, urgency +0.15 | Establishes worst-case plan |
| `healthy_baseline` | all disease facts removed | Counterfactual null |

For each scenario, `plan_delta` (difference in step count) and `cf_urgency` vs `original_urgency` are returned. The `plan_delta` value is a quantitative measure of intervention cost under different conditions.

---

## 4. Experimental Results

### 4.1 Classification Performance

| Metric | Value |
|---|---|
| Top-1 Test Accuracy | **96.8%** |
| Top-3 Test Accuracy | **99.1%** |
| Model Parameters | 5.3M |
| Training Epochs to Convergence | 18 / 25 |
| Best Validation Loss | 0.142 |

The lowest per-class F1 score was Pepper Bacterial Spot (0.934), which shows visual overlap with Tomato Bacterial Spot. The highest was Corn Common Rust (0.988), whose orange pustule pattern is highly distinctive.

### 4.2 Spatial Explanation Quality

Across 200 test images, Pearson correlation between `focus_score` and prediction confidence was r = 0.74 (p < 0.001). This validates the spatial-to-symbolic mapping: higher-confidence predictions correspond to sharper, more localised spatial attention.

A qualitative comparison of Grad-CAM++ vs LIME vs SHAP showed:
- SHAP: most localised, concentrated on disease lesion boundaries
- Grad-CAM++: global infected region, most visually interpretable
- LIME: sensitive to superpixel segmentation size parameter

### 4.3 Reasoning Engine

Across 150 test analyses, rules_fired showed strong positive correlation with urgency_score (r = 0.81). This validates internal consistency: more risk factors simultaneously present → more rules fire → higher urgency.

### 4.4 System Performance

| Metric | Value |
|---|---|
| Avg. full-analysis latency (CPU) | ~2.1s |
| Avg. GradCAM generation | ~0.8s |
| KG inference time | ~12ms |
| Symbolic fact extraction | ~2ms |
| Container RAM usage | ~1.2GB |
| API cold-start (HF Spaces) | ~45s |

The singleton orchestrator pattern reduces per-request latency from ~8s → ~2.1s by initialising all engines once at startup rather than per request.

---

## 5. Implementation Details

### 5.1 Backend Stack

| Component | Technology |
|---|---|
| API Framework | FastAPI 0.115 |
| Schema Validation | Pydantic v2 |
| ASGI Server | Uvicorn 1 worker |
| ML Framework | PyTorch 2.2 (CPU) |
| Vision Backbone | EfficientNet-B0 via timm |
| XAI | pytorch-grad-cam |
| Knowledge Graph | NetworkX 3.4 |
| Deployment | Docker on HuggingFace Spaces |

### 5.2 Key Engineering Decisions

**numpy==1.26.4 pin.** numpy 2.x introduced ABI breaking changes incompatible with the torch 2.2+cpu wheel. Explicitly pinning to 1.26.4 before torch installation prevents pip from resolving numpy 2.x.

**Three-step Docker install order.** Installing numpy → torch (CPU) → all other dependencies in separate RUN layers prevents version conflicts and leverages Docker layer caching.

**`register_full_backward_hook`.** Used throughout the XAI engine instead of the deprecated `register_backward_hook`. Hooks are always released in `finally` blocks.

**Singleton pattern.** The Orchestrator, VisionEngine, XAIEngine, ReasoningEngine, and PlanningEngine are all implemented as singletons, initialised once during FastAPI's lifespan event.

### 5.3 Frontend Stack

| Component | Technology |
|---|---|
| Framework | React 19 |
| Styling | Tailwind CSS 4 |
| HTTP Client | Axios |
| Routing | React Router v7 |
| Build Tool | Vite 7 |
| Deployment | Vercel |

---

## 6. Limitations

1. **Closed-world assumption.** The knowledge graph covers the 15 PlantVillage disease classes. An unseen disease class produces degraded reasoning quality — the system will classify it as the nearest known class and proceed with potentially inaccurate symbolic facts.

2. **Confidence propagation is heuristic.** Confidence values are multiplied through rule chains as a simplification of proper probabilistic inference. A Markov Logic Network or probabilistic soft logic approach would be more principled.

3. **Seasonal modifier is static.** Currently configured at deployment time. A production system would infer season from GPS coordinates and date automatically.

4. **CPU latency.** ~2.1s per full analysis is acceptable for single-image use but would not scale to batch processing without GPU acceleration or asynchronous inference workers.

5. **PlantVillage domain.** The dataset consists of controlled laboratory images. Performance on field photographs (variable lighting, partial leaf visibility, multiple diseases present) has not been systematically evaluated.

---

## 7. Phase 6 — Planned Work

Phase 6 will add a **grounded LLM explanation layer** that converts the symbolic reasoning trace into fluent natural language. The critical design constraint:

> The LLM performs no reasoning. It only explains, teaches, and reformulates — based on facts already verified by the symbolic engine.

This constraint prevents hallucination by construction. The LLM receives a structured JSON trace and generates an explanation grounded exclusively in that trace.

A planned **reasoning alignment evaluation** will compare symbolic explanations against LLM-generated explanations on three metrics: factual consistency, hallucination rate, and completeness. This evaluation is a potential paper contribution.

See `docs/research_notes/future_work.md` for full module descriptions.

---

## 8. Conclusion

ExplainPlan Vision demonstrates that deep learning, gradient-based explainability, symbolic reasoning, and adaptive planning can be integrated into a single coherent system without sacrificing the interpretability that makes each component valuable. The grounding pipeline — the conversion of neural outputs into verifiable first-order logic facts — is the architectural decision that makes full traceability possible.

The system is deployed and publicly accessible, making it immediately reproducible by other researchers. The research documentation, architecture diagrams, and per-phase findings included in this repository provide the scaffolding for a journal or conference submission.

---

## References

Chattopadhay, A., Sarkar, A., Howlader, P., & Balasubramanian, V. N. (2018). Grad-CAM++: Improved visual explanations for deep convolutional networks. *WACV 2018.*

Evans, R., & Grefenstette, E. (2018). Learning explanatory rules from noisy data. *Journal of Artificial Intelligence Research, 61*, 1-64.

FAO (2021). *The State of Food and Agriculture 2021.* Food and Agriculture Organization of the United Nations.

Garcez, A. d., Lamb, L. C., & Gabbay, D. M. (2022). *Neural-Symbolic Cognitive Reasoning.* Springer.

Hughes, D., & Salathé, M. (2015). An open access repository of images on plant health to enable the development of mobile disease diagnostics. *arXiv:1511.08060.*

Lundberg, S. M., & Lee, S.-I. (2017). A unified approach to interpreting model predictions. *NeurIPS 2017.*

Mohanty, S. P., Hughes, D. P., & Salathé, M. (2016). Using deep learning for image-based plant disease detection. *Frontiers in Plant Science, 7*, 1419.

Ribeiro, M. T., Singh, S., & Guestrin, C. (2016). "Why should I trust you?": Explaining the predictions of any classifier. *KDD 2016.*

Rocktäschel, T., & Riedel, S. (2017). End-to-end differentiable proving. *NeurIPS 2017.*

Sabbadin, R., Peyrard, N., & Sabbadin, B. (2021). A framework for automated planning of crop management. *Computers and Electronics in Agriculture, 184.*

Selvaraju, R. R., Cogswell, M., Das, A., Vedantam, R., Parikh, D., & Batra, D. (2017). Grad-CAM: Visual explanations from deep networks via gradient-based localization. *ICCV 2017.*

Tan, M., & Le, Q. (2019). EfficientNet: Rethinking model scaling for convolutional neural networks. *ICML 2019.*

---

*Technical Report TR-2026-01 · ExplainPlan Vision · Muhammad Aqib Niazi · 2026*
