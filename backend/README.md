# ExplainPlan-Vision — Backend API

FastAPI backend for the Explainable Neuro-Symbolic Visual Planning Agent.
Accepts leaf images and returns complete disease analysis with Grad-CAM explanation,
treatment planning, counterfactual reasoning, and human-adaptive explanations.

---

## Quick start

### 1. Place model assets

Download from your Phase 1 Kaggle notebook output:

```
assets/
├── best_model.pth          ← Phase 1 checkpoint (~20 MB)
└── class_mappings.json     ← Phase 1 class mappings
```

### 2. Create virtual environment

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment (optional)

```bash
cp .env.example .env
# Edit .env if you need to change device, thresholds, or CORS origins
```

### 4. Start the server

```bash
uvicorn backend.main:app --reload --port 8000
```

Server is ready at `http://localhost:8000`.

---

## API endpoints

All endpoints are under `/api/v1`.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/health` | Server status and model info |
| POST | `/api/v1/predict` | Disease prediction only |
| POST | `/api/v1/explain` | Prediction + Grad-CAM++ heatmap |
| POST | `/api/v1/plan` | Prediction + treatment plan |
| **POST** | **`/api/v1/full-analysis`** | **Complete pipeline — use this from React** |
| GET | `/api/v1/memory` | Temporal observation history |
| DELETE | `/api/v1/memory` | Clear observation history |
| GET | `/api/v1/knowledge-graph` | Knowledge graph metadata |

---

## How to test your APIs

### Option A — Swagger UI (easiest)

Open `http://localhost:8000/docs` in your browser.
Click any endpoint → "Try it out" → upload an image → "Execute".
You see the full request, response, and schema in one place.

### Option B — curl (terminal)

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Predict disease from an image
curl -X POST http://localhost:8000/api/v1/predict \
  -F "file=@/path/to/your/leaf.jpg"

# Full analysis — main endpoint for React frontend
curl -X POST http://localhost:8000/api/v1/full-analysis \
  -F "file=@/path/to/your/leaf.jpg" | python -m json.tool

# Get temporal memory state
curl http://localhost:8000/api/v1/memory

# Clear memory between sessions
curl -X DELETE http://localhost:8000/api/v1/memory
```

### Option C — Postman

1. Open Postman → New Request
2. Set method to POST, URL to `http://localhost:8000/api/v1/full-analysis`
3. Select Body → form-data
4. Add key `file`, type `File`, upload a JPG leaf image
5. Click Send

Import the full OpenAPI spec directly:
- Postman → Import → Link → `http://localhost:8000/openapi.json`
- All endpoints appear with correct schema automatically.

### Option D — Python script

```python
import requests

url   = "http://localhost:8000/api/v1/full-analysis"
files = {"file": ("leaf.jpg", open("leaf.jpg", "rb"), "image/jpeg")}
resp  = requests.post(url, files=files)
data  = resp.json()

print(data["prediction"]["disease_type"])
print(data["prediction"]["confidence"])
print(data["plan"]["overall_urgency"])
print(data["explanations"]["farmer"])
```

### Option E — pytest

```bash
# Run tests that do not need model weights (always works)
pytest tests/ -v -m "not requires_model"

# Run all tests including model-dependent ones (needs assets/)
pytest tests/ -v
```

---

## Response schema for `/api/v1/full-analysis`

```json
{
  "request_id": "a3f2b1c4",
  "processing_time_ms": 2341.0,

  "prediction": {
    "disease": "Tomato___Late_blight",
    "disease_type": "Late blight",
    "plant": "Tomato",
    "confidence": 0.9162,
    "severity": "high",
    "is_healthy": false,
    "top3": [{"disease_class": "...", "confidence": 0.92}, ...],
    "image_b64": "<base64 PNG of resized input image>"
  },

  "xai": {
    "gradcam_overlay_b64": "<base64 PNG — Grad-CAM heatmap on image>",
    "heatmap_b64": "<base64 PNG — raw jet-colourmap heatmap>",
    "infection_spread": "widespread",
    "focus_score": 0.1823,
    "activation_entropy": 3.91
  },

  "reasoning": {
    "symbolic_facts": [{"predicate": "disease_is", "arguments": [...], ...}],
    "inferences": [{"predicate": "must_isolate", "rule_fired": "...", ...}],
    "urgency_level": "immediate",
    "urgency_score": 8.24,
    "spread_risk": "critical",
    "treatment_class": "systemic_fungicide",
    "requires_isolation": true,
    "rules_fired": 9
  },

  "plan": {
    "overall_urgency": "critical",
    "actions": [
      {"step": 1, "action": "Immediately isolate affected plants", "urgency": "critical", "category": "containment"},
      {"step": 2, "action": "Apply systemic fungicide within 24 hours", "urgency": "critical", "category": "chemical"}
    ],
    "escalation_flag": false,
    "confidence_note": "High confidence (91.6%) — plan is reliable.",
    "monitoring_interval": "...",
    "inference_trace": ["isolation_mandate: must_isolate rule fired", ...]
  },

  "counterfactuals": [
    {"scenario": "lower_severity", "plan_delta": -2, "original_urgency": "immediate", "cf_urgency": "high", "narrative": "..."},
    {"scenario": "earlier_detection", ...},
    {"scenario": "lower_confidence", ...},
    {"scenario": "optimal_environment", ...}
  ],

  "decision_tree": {"step": 0, "urgency": 5, "probability": 1.0, "children": [...]},
  "expected_urgency": 3.42,

  "explanations": {
    "farmer":     "PLANT HEALTH REPORT\nYour Tomato plant has Late Blight...",
    "agronomist": "AGRONOMIC TREATMENT PLAN\nDiagnosis: Late Blight...",
    "researcher": "ExplainPlan-Vision — Neuro-Symbolic Reasoning Report..."
  },

  "trend": {
    "severity_trend": "stable",
    "spread_trend": "stable",
    "n_observations": 3,
    "summary": "..."
  }
}
```

---

## Connecting to React

In your React app:

```javascript
// POST a leaf image to the full-analysis endpoint
const formData = new FormData();
formData.append("file", imageFile);

const response = await fetch("http://localhost:8000/api/v1/full-analysis", {
  method: "POST",
  body: formData,
});
const data = await response.json();

// Display the Grad-CAM overlay image
// data.xai.gradcam_overlay_b64 is a base64 PNG
<img src={`data:image/png;base64,${data.xai.gradcam_overlay_b64}`} />

// Show treatment steps
data.plan.actions.forEach(action => console.log(action.step, action.action));

// Show farmer explanation
console.log(data.explanations.farmer);
```

CORS is already configured for `localhost:3000` (Create React App) and
`localhost:5173` (Vite). To add a production domain, update `EP_CORS_ORIGINS`
in `.env`.

---

## Docker

```bash
docker build -t explainplan-vision .
docker run -p 8000:8000 -v $(pwd)/assets:/app/assets explainplan-vision
```

---

## Project structure

```
explainplan/
├── backend/
│   ├── main.py                  ← FastAPI app, lifespan, CORS, middleware
│   ├── config.py                ← All settings (override via EP_* env vars)
│   ├── api/
│   │   └── routes.py            ← All 8 endpoint handlers
│   ├── vision/
│   │   └── model.py             ← EfficientNet-B0 singleton
│   ├── xai/
│   │   └── gradcam.py           ← Grad-CAM++ engine
│   ├── reasoning/
│   │   ├── facts.py             ← Symbolic fact extractor
│   │   ├── knowledge_graph.py   ← Disease knowledge graph
│   │   └── engine.py            ← Forward-chaining inference (20 rules)
│   ├── planning/
│   │   ├── engine.py            ← Adaptive plan generator
│   │   ├── counterfactual.py    ← 4 counterfactual scenarios
│   │   └── decision_tree.py     ← Probabilistic look-ahead planner
│   ├── memory/
│   │   └── temporal.py          ← Rolling observation memory
│   ├── services/
│   │   ├── orchestrator.py      ← 10-stage pipeline controller
│   │   └── explainer.py         ← farmer / agronomist / researcher modes
│   ├── schemas/
│   │   └── responses.py         ← All Pydantic response models
│   └── utils/
│       ├── image.py             ← Image loading, validation, base64
│       └── logger.py            ← Loguru setup
├── tests/
│   └── test_api.py              ← pytest integration tests
├── assets/                      ← Place model weights here (git-ignored)
├── logs/                        ← Runtime logs (git-ignored)
├── requirements.txt
├── Dockerfile
└── .env.example
```
