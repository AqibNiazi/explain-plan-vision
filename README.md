<div align="center">

<img src="https://img.shields.io/badge/PyTorch-2.2-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white"/>
<img src="https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
<img src="https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black"/>
<img src="https://img.shields.io/badge/TailwindCSS-4.0-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white"/>
<img src="https://img.shields.io/badge/Docker-Deployed-2496ED?style=for-the-badge&logo=docker&logoColor=white"/>
<img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge"/>

<br/><br/>

# ExplainPlan Vision
### *An Explainable Neuro-Symbolic Visual Planning Agent for Plant Disease Diagnosis*

<br/>

> **Research Note:** This system is developed for academic research purposes.
> All disease classifications and treatment plans should be validated by a qualified agronomist before operational use.

</div>

---

## Table of Contents

- [Overview](#overview)
- [Live Demo](#live-demo)
- [Research Motivation](#research-motivation)
- [System Architecture](#system-architecture)
- [The 10-Stage Pipeline](#the-10-stage-pipeline)
- [Dataset](#dataset)
- [Vision Model](#vision-model)
- [Explainability — Grad-CAM++](#explainability--grad-cam)
- [Neuro-Symbolic Reasoning](#neuro-symbolic-reasoning)
- [Adaptive Planning](#adaptive-planning)
- [Temporal Memory](#temporal-memory)
- [Performance](#performance)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [API Reference](#api-reference)
- [Deployment](#deployment)
- [Research Roadmap](#research-roadmap)
- [Citation](#citation)
- [License](#license)

---

## Overview

**ExplainPlan Vision** is a full-stack research system that diagnoses plant leaf disease from a single image and produces a complete, traceable explanation of every decision made — from the pixel level to the treatment plan.

The system integrates five distinct AI paradigms into a single inference pipeline:

| Paradigm | Component | Role |
|---|---|---|
| Deep Learning | EfficientNet-B0 | Visual classification of 15 disease classes |
| Gradient-Based XAI | Grad-CAM++ | Spatial explanation of *where* the model looks |
| Symbolic AI | First-Order Logic Facts | Grounding neural outputs in verifiable propositions |
| Knowledge Graph Reasoning | NetworkX + 20+ Inference Rules | Deriving urgency, spread risk, and treatment class |
| Adaptive Planning | 6-Context Plan Engine | Generating a numbered, annotated treatment plan |

A single POST to `/api/v1/full-analysis` returns all of these simultaneously — prediction, heatmap, reasoning trace, adaptive plan, counterfactual analysis, decision tree look-ahead, temporal trend, and three audience-specific natural language explanations.

**What distinguishes this project from a standard image classifier:**

1. The neural model output is *grounded* — converted to verifiable symbolic facts before any planning decision is made.
2. The reasoning is *traceable* — every treatment step references the inference rule that triggered it.
3. The explanations are *adaptive* — different outputs for a farmer, an agronomist, and a researcher.
4. The system *learns over time* — temporal memory tracks disease progression across sessions and flags worsening trends.

---

## Live Demo

| Service | URL |
|---|---|
| Frontend (Vercel) | https://explain-plan-frontend.vercel.app |
| Backend API (HF Spaces) | https://aqibniazi-explainplan-vision-api.hf.space |
| Swagger UI | https://aqibniazi-explainplan-vision-api.hf.space/docs |
| Training Notebook (Kaggle) | *(link to Kaggle notebook)* |

---

## Research Motivation

Plant disease causes an estimated **20–40% of global crop yield loss** annually (FAO, 2021). Early, accurate, and actionable diagnosis is critical — but it requires specialist knowledge that most smallholder farmers lack access to.

Deep learning models have demonstrated strong performance on plant disease classification, but two fundamental gaps remain:

**Gap 1 — Explainability.** A model that says *"Late Blight, 97% confidence"* provides no actionable information about *why* that conclusion was reached, *which regions* of the leaf were diagnostic, or *how certain* the model is about the spatial evidence.

**Gap 2 — Planning.** Classification is not treatment. A farmer needs to know *what to do*, *how urgently*, *in what order*, and *what would happen* if they wait.

**ExplainPlan Vision addresses both gaps** by combining a vision backbone with Grad-CAM++ spatial explanation, a neuro-symbolic reasoning layer that derives urgency and treatment class from verifiable facts, and an adaptive planning engine that produces a prioritised, annotated treatment plan.

The core research contribution is the *grounding pipeline* — the explicit conversion of neural outputs into first-order logic facts before any symbolic inference is performed. This is what makes the system's reasoning auditable in a way that a pure neural approach cannot be.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                            │
│   React 19 + Tailwind CSS 4 + Recharts + Lucide + Axios         │
│   ┌──────────┐  ┌──────────────┐  ┌────────────┐  ┌─────────┐  │
│   │ HomePage │  │ AnalyzePage  │  │ MemoryPage │  │  About  │  │
│   └──────────┘  └──────────────┘  └────────────┘  └─────────┘  │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTP REST  (multipart/form-data · JSON)
┌─────────────────────────▼───────────────────────────────────────┐
│                         API LAYER                               │
│   FastAPI 0.115 + Pydantic v2 + Uvicorn                         │
│   8 endpoints · singleton Orchestrator · Pydantic schemas       │
└──────────────────┬──────────────────────────────────────────────┘
                   │
       ┌───────────┴────────────┐
       │     ORCHESTRATOR       │
       │  Initialises engines   │
       │  at startup (once)     │
       └─┬──────┬──────┬──────┬─┘
         │      │      │      │
    Vision   XAI  Reasoning Planning
    Engine  Engine  Engine   Engine
```

See [`docs/architecture/system_overview.md`](docs/architecture/system_overview.md) for the complete data-flow diagram.

---

## The 10-Stage Pipeline

Every call to `/api/v1/full-analysis` executes all ten stages in sequence:

| Stage | Component | Output |
|---|---|---|
| 01 | EfficientNet-B0 Vision | Disease class, confidence, top-3, severity |
| 02 | Grad-CAM++ XAI | Heatmap (base64), focus score, entropy, spread |
| 03 | Symbolic Fact Extraction | First-order logic predicates with confidence |
| 04 | Knowledge Graph Inference | Urgency score, spread risk, treatment class |
| 05 | Temporal Memory Update | Trend analysis (improving / stable / worsening) |
| 06 | Adaptive Plan Generation | Numbered steps, 6 context mechanisms |
| 07 | Counterfactual Analysis | 4 what-if scenarios with plan deltas |
| 08 | Decision Tree Look-ahead | Expected urgency via probabilistic branching |
| 09 | Human-Adaptive Explanations | Farmer / agronomist / researcher narratives |
| 10 | Unified Response Assembly | Single JSON object, all fields |

---

## Dataset

| Property | Details |
|---|---|
| Name | PlantVillage Disease Classification Dataset |
| Source | [Kaggle — PlantVillage Dataset](https://www.kaggle.com/datasets/emmarex/plantdisease) |
| Total Images | ~54,000 leaf images |
| Classes | 15 disease + healthy categories |
| Splits | 80% train / 10% val / 10% test |

**Class Distribution (selected):**

| Class | Category |
|---|---|
| Tomato Late Blight | Fungal |
| Tomato Early Blight | Fungal |
| Tomato Leaf Mold | Fungal |
| Tomato Bacterial Spot | Bacterial |
| Potato Early Blight | Fungal |
| Potato Late Blight | Fungal |
| Corn Common Rust | Fungal |
| Pepper Bacterial Spot | Bacterial |
| Tomato Healthy | Healthy |
| *(+ 6 more)* | |

**Preprocessing Pipeline:**

```python
transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],   # ImageNet statistics
        std =[0.229, 0.224, 0.225]
    )
])
```

Training augmentations: random horizontal flip, random rotation (±15°), colour jitter.

---

## Vision Model

**Architecture:** EfficientNet-B0 (Tan & Le, 2019) with transfer learning from ImageNet weights.

```
EfficientNet-B0 Backbone (ImageNet pre-trained)
    └── MBConv blocks × 7
            └── Global Average Pooling
                    └── Dropout(0.2)
                            └── Linear(1280 → 15)  ← fine-tuned classifier head
```

**Training Configuration:**

| Hyperparameter | Value |
|---|---|
| Optimiser | Adam |
| Learning Rate | 1e-4 (with ReduceLROnPlateau) |
| Epochs | 25 |
| Batch Size | 32 |
| Loss Function | CrossEntropyLoss |
| Pre-trained Weights | ImageNet (torchvision) |
| Platform | Kaggle (GPU T4) |

**Why EfficientNet-B0 over ResNet50:**
EfficientNet-B0 achieves comparable accuracy to ResNet50 with 5.3M parameters vs 25.6M, making it substantially more suitable for CPU inference in the deployed HuggingFace Space without sacrificing classification performance.

---

## Explainability — Grad-CAM++

Grad-CAM++ (Chattopadhay et al., 2018) extends Grad-CAM by using a weighted combination of second-order gradients to produce more precise localisation, particularly for multiple object instances in a single image.

**Weighting formula:**

$$
\alpha_{ij}^{kc} = \frac{\frac{\partial^2 y^c}{(\partial A_{ij}^k)^2}}{2\frac{\partial^2 y^c}{(\partial A_{ij}^k)^2} + \sum_{a,b} A_{ab}^k \frac{\partial^3 y^c}{(\partial A_{ij}^k)^3}}
$$

**Spatial statistics extracted from heatmap:**

| Statistic | Definition | Interpretation |
|---|---|---|
| `infection_spread` | Fraction of heatmap above activation threshold | localised / moderate / widespread |
| `focus_score` | Peak-to-mean activation ratio | Higher = model more certain about location |
| `activation_entropy` | Shannon entropy of normalised heatmap | Lower = sharper, more confident localisation |

**Implementation note:** `register_full_backward_hook` is used throughout. GradCAM hooks are always removed in a `finally` block to prevent state leakage between concurrent requests.

---

## Neuro-Symbolic Reasoning

The reasoning layer converts the neural model's continuous outputs into discrete, verifiable symbolic facts, then applies inference rules over a disease knowledge graph.

### Symbolic Fact Extraction

```python
# Example facts extracted from a Late Blight prediction
[
  {"predicate": "disease_detected",   "arguments": ["tomato_late_blight"], "confidence": 0.97},
  {"predicate": "confidence_level",   "arguments": ["high"],               "confidence": 0.97},
  {"predicate": "severity_level",     "arguments": ["high"],               "confidence": 0.85},
  {"predicate": "infection_spread",   "arguments": ["widespread"],         "confidence": 0.91},
  {"predicate": "disease_type",       "arguments": ["fungal"],             "confidence": 1.00},
  {"predicate": "focus_score",        "arguments": ["0.723"],              "confidence": 0.91},
]
```

### Knowledge Graph Inference

The disease knowledge graph is built with NetworkX. 20+ inference rules fire over the graph to derive:

| Derived Fact | Example |
|---|---|
| `urgency_score` | 0.87 (continuous, 0–1) |
| `urgency_level` | `critical` |
| `spread_risk` | `high` |
| `treatment_class` | `fungicide` |
| `requires_isolation` | `true` |
| `rules_fired` | 14 |

**Example rule (pseudocode):**

```
IF disease_type(X, fungal)
AND severity_level(X, high)
AND infection_spread(X, widespread)
THEN urgency_level(X, critical) WITH confidence 0.95
AND requires_isolation(X, true) WITH confidence 0.90
```

---

## Adaptive Planning

The planning engine adapts treatment steps based on 6 simultaneous context mechanisms:

| Mechanism | Influence |
|---|---|
| Disease type (fungal / bacterial / viral) | Determines treatment class (fungicide / antibiotic / cultural) |
| Infection spread (localised / moderate / widespread) | Scales isolation and containment steps |
| Urgency score (continuous) | Determines step ordering and time constraints |
| Seasonal modifier | Adjusts chemical application frequency |
| Severity level | Adds or removes monitoring steps |
| Temporal trend | Escalates plan if worsening trend detected |

**Example plan action:**

```json
{
  "step": 1,
  "action": "Immediately isolate affected plants to prevent spread to neighbouring rows.",
  "category": "containment",
  "urgency": "critical",
  "time_constraint": "within 24 hours"
}
```

### Counterfactual Analysis

4 what-if scenarios are computed for every analysis:

| Scenario | Description |
|---|---|
| `early_detection` | How would the plan differ if caught 2 weeks earlier? |
| `isolated_spread` | What if infection were localised rather than widespread? |
| `critical_severity` | What if severity were at maximum? |
| `healthy_baseline` | What would a healthy plant's plan look like? |

Each scenario returns `plan_delta` (step count difference) and `cf_urgency` vs `original_urgency`.

---

## Temporal Memory

The system maintains a sliding-window memory of past analyses for the same plant/session. On each new analysis, trend detection compares the current observation against history:

| Trend Field | Values | Trigger |
|---|---|---|
| `severity_trend` | improving / stable / worsening | Change in severity score across window |
| `urgency_trend` | improving / stable / worsening | Change in urgency_score across window |
| `spread_trend` | improving / stable / worsening | Change in infection_spread category |
| `disease_stable` | boolean | Whether the same disease class persists |

The `monitoring_interval` recommendation adjusts based on trend: daily if worsening, weekly if stable, bi-weekly if improving.

---

## Performance

| Metric | Value |
|---|---|
| Top-1 Classification Accuracy | 96.8% |
| Top-3 Classification Accuracy | 99.1% |
| Model Parameters | 5.3M (EfficientNet-B0) |
| Avg. Full-Analysis Latency (CPU) | ~2.1s |
| Avg. GradCAM Generation Time | ~0.8s |
| Knowledge Graph Inference Time | ~12ms |
| API cold-start (HF Spaces) | ~45s (model loading) |

---

## Project Structure

```
ExplainPlan-Vision/
│
├── 📓 notebooks/
│   ├── phase1_vision_foundation/       # EfficientNet training + evaluation
│   ├── phase2_xai/                     # Grad-CAM++ + LIME + SHAP (offline)
│   ├── phase3_planning/                # Adaptive plan engine prototyping
│   └── phase4_neurosymbolic/           # KG construction + rule writing
│
├── ⚙️ backend/
│   ├── main.py                         # FastAPI app factory + lifespan
│   ├── config.py                       # Pydantic-settings: device, paths, CORS
│   ├── api/
│   │   └── routes.py                   # All 8 endpoints
│   ├── vision/
│   │   └── model.py                    # EfficientNet-B0 loader + inference
│   ├── xai/
│   │   └── gradcam.py                  # Grad-CAM++ + spatial statistics
│   ├── reasoning/
│   │   └── engine.py                   # Fact extraction + KG inference
│   ├── planning/
│   │   └── planner.py                  # Adaptive plan + counterfactuals
│   ├── memory/
│   │   └── temporal.py                 # Sliding-window memory + trends
│   ├── services/
│   │   └── orchestrator.py             # Singleton pipeline coordinator
│   ├── schemas/
│   │   └── responses.py                # Pydantic v2 response models
│   └── utils/
│       └── logger.py                   # Loguru setup
│
├── 🖥️ frontend/
│   ├── src/
│   │   ├── services/
│   │   │   ├── apiClient.js            # Axios instance + endpoint map
│   │   │   └── analysisService.js      # All API call functions
│   │   ├── hooks/
│   │   │   ├── useAnalysis.js          # Upload + result state management
│   │   │   └── useHealth.js            # Backend status polling
│   │   ├── pages/
│   │   │   ├── HomePage.jsx            # Hero, feature grid, pipeline viz
│   │   │   ├── AnalyzePage.jsx         # Upload + 10-stage result display
│   │   │   ├── MemoryPage.jsx          # Temporal memory viewer
│   │   │   └── AboutPage.jsx           # Pipeline docs + API reference
│   │   ├── components/
│   │   │   ├── analysis/               # PredictionCard, XAICard, ReasoningCard …
│   │   │   ├── layout/                 # Navbar (live status), Footer
│   │   │   └── ui/                     # ImageUploader, reusable primitives
│   │   ├── layout/
│   │   │   └── AppLayout.jsx
│   │   ├── routes/
│   │   │   └── AppRoutes.jsx
│   │   └── utils/
│   │       └── helpers.js
│   ├── vite.config.js                  # Dev proxy: /api → backend
│   └── package.json
│
├── 🐳 Dockerfile                       # HuggingFace Spaces deployment
├── startup.py                          # Weight download at container startup
├── assets/
│   ├── best_model.pth                  # EfficientNet-B0 fine-tuned weights
│   └── class_mappings.json             # Index → disease class mapping
│
├── docs/
│   ├── architecture/
│   │   └── system_overview.md          # Full data-flow diagrams
│   └── research_notes/
│       └── phase_roadmap.md            # Phase 1–7 roadmap with rationale
│
├── .gitignore
├── LICENSE                             # MIT + research disclaimer
└── README.md
```

---

## Installation & Setup

### Prerequisites

| Tool | Version |
|---|---|
| Python | ≥ 3.10 |
| Node.js | ≥ 18.0 |
| npm | ≥ 9.0 |
| Git + git-lfs | latest |

### 1. Clone

```bash
git clone https://github.com/AqibNiazi/ExplainPlan-Vision.git
cd ExplainPlan-Vision
```

### 2. Backend

```bash
cd backend

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

# Place trained weights
cp ~/Downloads/best_model.pth      ../assets/best_model.pth
cp ~/Downloads/class_mappings.json ../assets/class_mappings.json

uvicorn backend.main:app --reload --port 8000
# → http://localhost:8000/docs
```

### 3. Frontend

```bash
cd frontend
npm install

# Configure backend URL
cp .env.example .env
# VITE_API_URL=   (leave blank — Vite proxy handles dev)

npm run dev
# → http://localhost:5173
```

### 4. Training Notebook

1. Upload the relevant notebook from `notebooks/` to Kaggle
2. Attach the PlantVillage dataset
3. Enable GPU (T4 recommended)
4. Run all cells in order
5. Download `best_model.pth` and `class_mappings.json` from `/kaggle/working/`

---

## API Reference

**Base URL (local):** `http://127.0.0.1:8000`  
**Base URL (production):** `https://aqibniazi-explainplan-vision-api.hf.space`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Server status, model loaded flag, device, version |
| `POST` | `/api/v1/predict` | Classification only (no XAI) |
| `POST` | `/api/v1/explain` | Grad-CAM++ only |
| `POST` | `/api/v1/plan` | Treatment plan only |
| `POST` | `/api/v1/full-analysis` | **Complete 10-stage pipeline** ← primary endpoint |
| `GET` | `/api/v1/memory` | Temporal memory state + trends |
| `DELETE` | `/api/v1/memory` | Clear temporal memory |
| `GET` | `/api/v1/knowledge-graph` | Knowledge graph metadata |

### `GET /api/v1/health`

```json
{
  "status": "ok",
  "version": "1.0.0",
  "device": "cpu",
  "model_loaded": true,
  "num_classes": 15
}
```

### `POST /api/v1/full-analysis`

**Request:** `multipart/form-data` — field `file` (JPEG / PNG / WebP, max 10 MB)

**Response (abbreviated):**
```json
{
  "request_id": "uuid",
  "processing_time_ms": 2143,
  "prediction": {
    "disease": "Tomato Late Blight",
    "confidence": 0.974,
    "severity": "high",
    "is_healthy": false,
    "top3": [...]
  },
  "xai": {
    "gradcam_overlay_b64": "...",
    "infection_spread": "widespread",
    "focus_score": 0.723,
    "activation_entropy": 1.241
  },
  "reasoning": {
    "symbolic_facts": [...],
    "urgency_level": "critical",
    "urgency_score": 0.87,
    "rules_fired": 14
  },
  "plan": {
    "actions": [...],
    "overall_urgency": "critical",
    "escalation_flag": true
  },
  "counterfactuals": [...],
  "explanations": {
    "farmer": "...",
    "agronomist": "...",
    "researcher": "..."
  },
  "trend": {
    "severity_trend": "worsening",
    "urgency_trend": "worsening",
    "disease_stable": true,
    "n_observations": 3
  }
}
```

Full schema available at `/docs` (Swagger UI) and `/redoc`.

---

## Deployment

### Backend — HuggingFace Spaces (Docker)

The backend is containerised with Docker and deployed on HuggingFace Spaces free tier (CPU Basic).

```dockerfile
FROM python:3.11-slim
# ...
EXPOSE 7860
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]
```

Model weights (`best_model.pth`, `class_mappings.json`) are committed to the Space repository under `assets/` and copied into the container at build time.

**Startup time:** ~45 seconds (model loading on cold start). HuggingFace Spaces sleep after 48 hours of inactivity — the first request after sleep takes ~60s.

### Frontend — Vercel

```bash
# Build
cd frontend && npm run build

# Set environment variable in Vercel dashboard:
VITE_API_URL=https://aqibniazi-explainplan-vision-api.hf.space
```

### CORS

Add your Vercel production domain to `backend/config.py`:

```python
cors_origins: List[str] = [
    "http://localhost:5173",
    "https://your-app.vercel.app",     # ← add this
]
```

---

## Research Roadmap

| Phase | Status | Description |
|---|---|---|
| 1 — Vision Foundation | ✅ Complete | EfficientNet-B0, 15 classes, 96.8% accuracy |
| 2 — XAI | ✅ Complete | Grad-CAM++, spatial statistics |
| 3 — Adaptive Planning | ✅ Complete | 6-context plan engine, counterfactuals |
| 4 — Neuro-Symbolic Reasoning | ✅ Complete | KG inference, symbolic fact extraction |
| 5 — Full-Stack Application | ✅ Complete | FastAPI backend, React frontend, Docker deployment |
| 6 — LLM Grounding Layer | 🔄 Planned | Grounded LLM explanation, reasoning alignment eval |
| 7 — Multi-Agent / PDDL | 🔲 Future | Formal planning integration |

See [`docs/research_notes/phase_roadmap.md`](docs/research_notes/phase_roadmap.md) for detailed module descriptions.

---

## Citation

If you use this codebase or reference this work in your research, please cite:

```bibtex
@software{explainplan_vision,
  author    = {Niazi, Muhammad Aqib},
  title     = {ExplainPlan Vision: An Explainable Neuro-Symbolic Visual
               Planning Agent for Plant Disease Diagnosis},
  year      = {2026},
  url       = {https://github.com/AqibNiazi/ExplainPlan-Vision},
  note      = {Software available at GitHub}
}
```

**Referenced Works:**

- Tan, M., & Le, Q. (2019). EfficientNet: Rethinking model scaling for convolutional neural networks. *ICML 2019*.
- Chattopadhay, A., et al. (2018). Grad-CAM++: Improved visual explanations for deep convolutional networks. *WACV 2018*.
- Selvaraju, R. R., et al. (2017). Grad-CAM: Visual explanations from deep networks. *ICCV 2017*.
- Hughes, D., & Salathé, M. (2015). An open access repository of images on plant health to enable the development of mobile disease diagnostics. *arXiv:1511.08060*.

---

## License

This project is licensed under the **MIT License** — see [`LICENSE`](LICENSE) for details.

The PlantVillage dataset is subject to its own terms of use on Kaggle. This software must not be used for commercial agricultural advisory services without appropriate validation by a qualified agronomist.

---

<div align="center">

Built by **Muhammad Aqib Niazi**

*If this project helped your research, please consider giving it a ⭐*

</div>
