# Changelog

All notable changes to ExplainPlan Vision are documented here.  
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.0.0] — 2026-06 — Full-Stack Production Release

### Added — Phase 5: Deployment
- FastAPI backend deployed on HuggingFace Spaces (Docker, port 7860)
- React 19 frontend deployed on Vercel with VITE_API_URL env config
- Vite dev proxy for zero-CORS local development
- `startup.py` for weight download at container startup
- `COPY assets/` in Dockerfile — weights baked into image at build time
- Health endpoint with model_loaded flag and version
- CORS configured for Vercel production domain

### Fixed
- `libgl1-mesa-glx` unavailable on Debian Trixie → replaced with `libgl1`
- `startup.py` missing from Docker build context → moved to repo root
- numpy 2.x ABI incompatibility with torch 2.2+cpu → pinned `numpy==1.26.4`
- torch CUDA wheel (~2.4GB) pulled on CPU-only container → explicit `+cpu` suffix
- `gcc` missing for `stringzilla` (albumentations dependency) → added to apt step
- assets/ folder not copied into Docker image → added `COPY --chown=user assets/`

---

## [0.4.0] — 2026-05 — Phase 4: Neuro-Symbolic Reasoning

### Added
- First-order logic fact extraction from vision + XAI outputs
- NetworkX disease knowledge graph with 15 disease nodes
- 20+ inference rules: disease-type, severity escalation, isolation, seasonal, temporal, composite urgency
- `urgency_score` (continuous 0–1), `urgency_level`, `spread_risk`, `treatment_class`, `requires_isolation`
- Human-adaptive explanations: farmer / agronomist / researcher
- Temporal memory with sliding-window trend analysis
- `severity_trend`, `urgency_trend`, `spread_trend` fields
- `monitoring_interval` recommendation based on trend

---

## [0.3.0] — 2026-04 — Phase 3: Adaptive Planning

### Added
- 6-context adaptive plan engine
- Numbered treatment steps with `category` and `urgency` per step
- `confidence_note` and `escalation_flag` in plan response
- Counterfactual analysis: 4 scenarios with `plan_delta` and `cf_urgency`
- Probabilistic decision tree look-ahead with `expected_urgency` scalar
- `monitoring_interval` field in plan response

---

## [0.2.0] — 2026-03 — Phase 2: Explainability

### Added
- Grad-CAM++ on EfficientNet-B0 final convolutional block
- `gradcam_overlay_b64` and `heatmap_b64` as base64 PNG in response
- Spatial statistics: `infection_spread`, `focus_score`, `activation_entropy`
- LIME superpixel explanation (Kaggle notebook only)
- SHAP GradientExplainer (Kaggle notebook only)
- `register_full_backward_hook` throughout — avoids PyTorch 2.x deprecation warning
- Hook cleanup in `finally` blocks to prevent state leakage between requests

---

## [0.1.0] — 2026-02 — Phase 1: Vision Foundation

### Added
- EfficientNet-B0 fine-tuned on PlantVillage (15 classes, ~54,000 images)
- Top-1 accuracy: 96.8% · Top-3 accuracy: 99.1%
- Calibrated softmax confidence
- Severity heuristic from confidence + class metadata
- `is_healthy` flag
- Top-3 alternative predictions
- `assets/best_model.pth` checkpoint export
- `assets/class_mappings.json` index→class mapping
- Kaggle training notebook with full pipeline
