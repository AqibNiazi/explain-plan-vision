# Phase 2 — Explainability (XAI): Findings & Observations

**Methods:** Grad-CAM++ (deployed), LIME (notebook), SHAP GradientExplainer (notebook)

---

## Objective

Produce spatial explanations that answer: *which regions of the leaf drove the classification decision?* The explanations must be (a) visually meaningful to a plant pathologist, (b) computationally feasible for real-time inference on CPU, and (c) machine-readable for extraction of spatial statistics that feed the reasoning engine.

---

## Methods Implemented and Compared

### Grad-CAM++ (Chattopadhay et al., 2018)

Extension of Grad-CAM that uses second-order gradient weighting, producing sharper localisation particularly when multiple infection sites are present on a single leaf.

**Deployed in production.** Average generation time on CPU: ~0.8s.

**Spatial statistics extracted:**

| Statistic | Formula | Interpretation |
|---|---|---|
| `infection_spread` | Fraction of heatmap pixels above threshold | localised (<20%) / moderate (20–50%) / widespread (>50%) |
| `focus_score` | peak_activation / mean_activation | Higher = model more confident about location |
| `activation_entropy` | Shannon entropy of normalised map | Lower = sharper, more discriminative localisation |

### LIME (Ribeiro et al., 2016)

Superpixel perturbation with local linear surrogate. Identifies *which image segments* contributed most to the prediction.

**Available in Kaggle notebook only.** Average generation time: ~45s (CPU). Too slow for real-time deployment.

### SHAP GradientExplainer (Lundberg & Lee, 2017)

Shapley value attribution using expected gradients. Pixel-level contribution scores satisfying consistency, local accuracy, and missingness axioms.

**Available in Kaggle notebook only.** Average generation time: ~120s (CPU).

**Key engineering note:** `shap.GradientExplainer` was used instead of `DeepExplainer` due to a known BatchNorm tensor size mismatch in DeepLIFT's handler for EfficientNet's BatchNorm layers. GradCAM hooks must be fully removed before initialising GradientExplainer to prevent hook state corruption.

---

## Comparative Findings

| Property | Grad-CAM++ | LIME | SHAP |
|---|---|---|---|
| Granularity | Feature-map level | Superpixel level | Pixel level |
| Localisation precision | Medium-high | Medium | High |
| Computational cost (CPU) | ~0.8s | ~45s | ~120s |
| Sensitivity to parameters | Low | High (segment size) | Medium |
| Deployable real-time | ✅ Yes | ❌ No | ❌ No |
| Machine-readable statistics | ✅ Yes | Partial | Partial |

### Observation 1 — SHAP is more localised; Grad-CAM++ is more global

SHAP pixel-level attribution concentrated on the precise boundaries of disease lesions — the dark brown ring edges of Late Blight, the yellow halo of Bacterial Spot. Grad-CAM++ produced broader activation regions covering the entire infected area.

**Implication:** For human explanation, Grad-CAM++ overlays are more immediately interpretable. For precision spatial analysis (measuring lesion area), SHAP would be preferred.

### Observation 2 — LIME is sensitive to superpixel segmentation size

Segment size 50 vs 100 superpixels produced materially different importance rankings for the same image. This sensitivity limits LIME's reliability for automated spatial statistics extraction — a human must visually inspect the output.

### Observation 3 — Grad-CAM++ focus_score correlates with model confidence

Across 200 test images, Pearson correlation between focus_score and prediction confidence: **r = 0.74** (p < 0.001). This confirms that higher-confidence predictions correspond to sharper, more localised spatial attention — the model "knows where to look" more precisely when it is confident.

**This correlation is used in the reasoning engine:** a high focus_score strengthens the `confidence_level(high)` symbolic fact.

### Observation 4 — activation_entropy distinguishes disease stages

Early-stage infections (small lesions, low spread) produce low entropy heatmaps (concentrated activation). Late-stage infections (widespread lesions) produce high entropy heatmaps. This directly maps to the `infection_spread` symbolic fact.

---

## Implementation Notes

- `register_full_backward_hook` used throughout (deprecated `register_backward_hook` removed in PyTorch 2.x)
- GradCAM hooks always removed in `finally` blocks to prevent state leakage between concurrent API requests
- Heatmap resized to original image dimensions with bilinear interpolation before overlay blending
- Overlay alpha: 0.5 (heatmap) + 0.5 (original) — tuned for visual clarity

---

## Key Conclusion

Grad-CAM++ is the correct XAI method for this deployment context: real-time CPU inference, machine-readable spatial statistics, and visually meaningful overlays. LIME and SHAP are retained in the Kaggle notebook for research comparison and potential paper inclusion.

The conversion of Grad-CAM++ statistics into symbolic facts (Stage 03) is the architectural decision that elevates this from a standard XAI system to a neuro-symbolic one: the spatial evidence becomes a *verifiable proposition* rather than a pixel array.
