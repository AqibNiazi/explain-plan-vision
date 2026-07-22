# API Design — ExplainPlan Vision

**Base URL (local):** `http://127.0.0.1:8000`  
**Base URL (production):** `https://aqibniazi-explainplan-vision-api.hf.space`  
**OpenAPI / Swagger:** `/docs`  
**ReDoc:** `/redoc`

---

## Design Principles

1. **Single-call full pipeline.** The primary endpoint `/api/v1/full-analysis` returns all 10 stages in one response. Clients do not need to chain multiple calls.

2. **Granular endpoints for research.** Individual endpoints (`/predict`, `/explain`, `/plan`) allow researchers to call specific stages in isolation for ablation studies.

3. **Pydantic v2 schemas everywhere.** All request and response bodies are validated by Pydantic v2 models. The `/docs` endpoint shows the complete schema.

4. **Singleton orchestrator.** All engines are initialised once at startup. Per-request latency is dominated by inference (~2.1s), not initialisation.

---

## Endpoint Reference

### `GET /api/v1/health`

Returns server liveness, model status, device, and API version.

**Response:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "device": "cpu",
  "model_loaded": true,
  "num_classes": 15
}
```

---

### `POST /api/v1/full-analysis` ← Primary Endpoint

**Request:** `multipart/form-data`, field `file` (JPEG/PNG/WebP, max 10MB)

**Response (complete schema):**

```json
{
  "request_id": "uuid4",
  "processing_time_ms": 2143.7,
  "expected_urgency": 0.87,

  "prediction": {
    "disease": "Tomato Late Blight",
    "disease_class": "Tomato___Late_blight",
    "plant": "Tomato",
    "disease_type": "fungal",
    "confidence": 0.974,
    "severity": "high",
    "is_healthy": false,
    "top3": [
      {"disease_class": "Tomato___Late_blight", "confidence": 0.974},
      {"disease_class": "Tomato___Early_blight", "confidence": 0.018},
      {"disease_class": "Tomato___Leaf_Mold", "confidence": 0.005}
    ]
  },

  "xai": {
    "gradcam_overlay_b64": "<base64 PNG string>",
    "heatmap_b64": "<base64 PNG string>",
    "infection_spread": "widespread",
    "focus_score": 0.723,
    "activation_entropy": 1.241
  },

  "reasoning": {
    "symbolic_facts": [
      {"predicate": "disease_detected", "arguments": ["tomato_late_blight"], "confidence": 0.974, "source": "vision"},
      {"predicate": "severity_level",   "arguments": ["high"],               "confidence": 0.85,  "source": "vision"},
      {"predicate": "infection_spread", "arguments": ["widespread"],         "confidence": 0.91,  "source": "xai"},
      "..."
    ],
    "inferences": ["urgency_level(critical)", "requires_isolation(true)", "..."],
    "urgency_level": "critical",
    "urgency_score": 0.87,
    "spread_risk": "high",
    "treatment_class": "fungicide",
    "requires_isolation": true,
    "escalation_flag": true,
    "rules_fired": 14
  },

  "plan": {
    "disease_type": "fungal",
    "overall_urgency": "critical",
    "actions": [
      {"step": 1, "action": "Isolate affected plants immediately.", "category": "containment", "urgency": "critical"},
      {"step": 2, "action": "Apply approved fungicide within 24 hours.", "category": "chemical", "urgency": "critical"},
      "..."
    ],
    "adaptations": ["Spread pattern (widespread) adds isolation step", "Trend (worsening) escalates monitoring"],
    "escalation_flag": true,
    "confidence_note": "High confidence prediction — plan reliability: high",
    "monitoring_interval": "daily"
  },

  "counterfactuals": [
    {
      "scenario": "early_detection",
      "description": "Detected 2 weeks earlier at lower severity",
      "original_urgency": "critical",
      "cf_urgency": "medium",
      "plan_delta": -4,
      "narrative": "Early detection would reduce required actions by 4 steps..."
    },
    "..."
  ],

  "explanations": {
    "farmer": "Your tomato plant has Late Blight, a serious fungal disease...",
    "agronomist": "Phytophthora infestans infection confirmed at high severity...",
    "researcher": "Symbolic reasoning trace: 14 rules fired. disease_type(fungal) ∧ severity(high) ∧ spread(widespread) → urgency(critical) [conf: 0.87]..."
  },

  "trend": {
    "severity_trend": "worsening",
    "urgency_trend": "worsening",
    "spread_trend": "stable",
    "disease_stable": true,
    "n_observations": 3,
    "latest_urgency": "critical",
    "latest_severity": "high",
    "summary": "Disease worsening over 3 observations. Immediate intervention required.",
    "monitoring_recommendation": "Monitor daily — worsening trend detected"
  }
}
```

---

### `POST /api/v1/predict`

Classification only. Skips XAI, reasoning, and planning. Useful for high-throughput batch screening.

**Response:** `prediction` field only (same schema as above).

---

### `POST /api/v1/explain`

Grad-CAM++ only. Returns heatmap and spatial statistics.

**Response:** `xai` field only.

---

### `POST /api/v1/plan`

Full pipeline minus `/predict` — assumes classification result is passed. Returns reasoning + plan.

---

### `GET /api/v1/memory`

Temporal memory state — all observations stored for current session.

**Response:**
```json
{
  "n_observations": 3,
  "capacity": 10,
  "entries": [...],
  "trend": {...},
  "monitoring_recommendation": "Monitor daily"
}
```

---

### `DELETE /api/v1/memory`

Clears the temporal memory store. Used when starting analysis of a new plant.

---

### `GET /api/v1/knowledge-graph`

Returns knowledge graph metadata: node count, edge count, disease nodes, rule count.

---

## Error Responses

| Code | Condition |
|---|---|
| 400 | No file, empty filename, unsupported file type |
| 413 | File exceeds 10MB limit |
| 422 | Pydantic validation error (malformed request) |
| 500 | Inference failure (model error, OOM, etc.) |

All errors return:
```json
{"detail": "human-readable message", "error_type": "ExceptionClassName"}
```
