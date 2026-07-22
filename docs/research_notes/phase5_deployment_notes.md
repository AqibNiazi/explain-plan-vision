# Phase 5 — Full-Stack Deployment: Notes & Decisions

---

## Objective

Expose the complete 10-stage pipeline as a production web application accessible from any browser, with no local setup required. The deployment must be free-tier compatible and handle CPU-only inference gracefully.

---

## Backend — FastAPI Design Decisions

### Singleton Orchestrator Pattern

All five engines (Vision, XAI, Reasoning, Planning, Memory) are initialised once at application startup inside the FastAPI `lifespan` context manager. They are stored as class-level singletons and reused for every request.

**Impact:** Reduces per-request latency from ~8.2s (cold initialisation) to ~2.1s (warm inference only).

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    Orchestrator.get()   # loads all engines once
    yield
    # cleanup on shutdown
```

**Trade-off:** Memory usage is ~1.2GB at rest (model loaded). This is acceptable for HuggingFace Spaces free tier (16GB limit) but would be a concern if running multiple workers.

### Why FastAPI over Flask

| Criterion | FastAPI | Flask |
|---|---|---|
| Pydantic v2 integration | Native | Manual |
| Auto OpenAPI / Swagger | Built-in | Extension required |
| Async support | Native | Limited |
| Type annotation validation | Built-in | Manual |
| Response schema generation | Automatic | Manual |

FastAPI's automatic Swagger UI at `/docs` was particularly valuable — professors and reviewers can inspect every endpoint, schema, and response model without reading source code.

### Pydantic v2 Response Models

Every response is validated by a Pydantic v2 model before being returned. This enforces schema consistency and makes the API contract machine-readable.

Key models: `PredictionResult`, `XAIResult`, `ReasoningResult`, `PlanResult`, `FullAnalysisResponse`.

---

## Deployment — HuggingFace Spaces (Docker)

### Port Configuration

HuggingFace Spaces requires port **7860** (not 8000). This was the first deployment blocker encountered. All internal references, health checks, and the Dockerfile `EXPOSE` directive use 7860.

### Dependency Installation Order

The correct installation order to avoid numpy/torch ABI conflicts:

```dockerfile
# 1 — numpy pinned first
RUN pip install numpy==1.26.4

# 2 — torch CPU wheel (avoids 2.4GB CUDA download)
RUN pip install torch==2.2.2+cpu torchvision==0.17.2+cpu \
    --extra-index-url https://download.pytorch.org/whl/cpu

# 3 — remaining dependencies
RUN pip install -r requirements.txt
```

**Why this order matters:** If torch is installed first, it may pull numpy 2.x as a dependency, which then conflicts with torch's compiled C extensions that expect the numpy 1.x ABI. Installing numpy 1.26.4 explicitly first locks the ABI before torch can override it.

### Build Issues Encountered and Fixed

| Issue | Root Cause | Fix |
|---|---|---|
| `libgl1-mesa-glx not found` | Package removed in Debian Trixie | Replace with `libgl1` |
| `startup.py not found` | File was inside `backend/` not repo root | Moved to repo root |
| `gcc not found` | `stringzilla` (albumentations dep) needs compiler | Added `gcc g++ python3-dev` to apt |
| `numpy not available` | torch pulled numpy 2.x, broke ABI | Pin `numpy==1.26.4`, install before torch |
| `class_mappings.json not found` | Dockerfile had no `COPY assets/` line | Added `COPY --chown=user assets/ ./assets/` |

### Model Weight Distribution

Model weights (`best_model.pth`, ~22MB) and class mappings (`class_mappings.json`, ~1KB) are committed directly to the Space repository under `assets/`. The `startup.py` script checks for their presence and downloads from HuggingFace Model Hub if missing — this provides a fallback for cases where the files are not in the repo.

### Cold Start Latency

HuggingFace Spaces free tier sleeps after 48 hours of inactivity. Cold start (Space wake-up + model loading) takes approximately **45–60 seconds**. Subsequent requests run at ~2.1s.

**Mitigation:** The health endpoint (`/api/v1/health`) returns quickly even during model loading, so the frontend can poll it and show a loading state rather than a blank error.

---

## Frontend — React 19 + Tailwind CSS 4

### Vite Proxy for CORS-Free Development

In development, Vite proxies all `/api/*` requests to `http://127.0.0.1:8000`, eliminating CORS issues entirely during local development:

```js
// vite.config.js
server: {
  proxy: {
    "/api": {
      target: process.env.VITE_API_URL || "http://127.0.0.1:8000",
      changeOrigin: true,
    }
  }
}
```

In production (Vercel), `VITE_API_URL` is set to the HuggingFace Space URL, and CORS is handled by the FastAPI middleware.

### Component Architecture

Seven dedicated analysis components, one per result domain:

| Component | Data Source |
|---|---|
| `PredictionCard` | `result.prediction` |
| `XAICard` | `result.xai` — tab switcher: overlay / heatmap / original |
| `ReasoningCard` | `result.reasoning` — expandable symbolic facts |
| `PlanCard` | `result.plan` — colour-coded by category |
| `CounterfactualsCard` | `result.counterfactuals` — scenario tab switcher |
| `ExplanationsCard` | `result.explanations` — farmer/agronomist/researcher |
| `TrendCard` | `result.trend` — improving/stable/worsening indicators |

### Custom Hook: `useAnalysis`

All upload state, progress tracking, error handling, and toast notifications are managed in a single `useAnalysis` hook. Pages contain zero business logic — they only render.

---

## Deployment — Vercel (Frontend)

Build command: `npm run build`  
Output directory: `dist/`  
Environment variable: `VITE_API_URL=https://aqibniazi-explainplan-vision-api.hf.space`

Vercel auto-deploys on every push to `main`. Build time: ~35 seconds.

### CORS Configuration

The FastAPI backend's `cors_origins` must include the Vercel production domain:

```python
cors_origins: List[str] = [
    "http://localhost:5173",
    "https://your-app.vercel.app",    # ← production domain
]
```

---

## Performance Summary

| Metric | Value |
|---|---|
| Backend cold start | ~50s |
| Backend warm request (full-analysis) | ~2.1s |
| GradCAM generation | ~0.8s |
| KG inference (20+ rules) | ~12ms |
| Frontend build size | ~420KB gzipped |
| Frontend initial load (Vercel CDN) | <1s |
| Model size on disk | ~22MB |
| Container RAM at rest | ~1.2GB |

---

## Lessons Learned

1. **Dependency installation order matters more than versions alone.** The numpy/torch ABI conflict was not solved by pinning versions — it required changing the installation order.

2. **HuggingFace Spaces Docker has undocumented constraints.** The port 7860 requirement, non-root user requirement (`useradd -m -u 1000 user`), and `/home/user` working directory are not prominently documented but are required for deployment to succeed.

3. **Singleton pattern is essential for ML APIs.** Loading a 22MB model on every request would make the API unusable. The lifespan-scoped singleton is the correct pattern for FastAPI + PyTorch.

4. **Separate install steps improve Docker cache utilisation.** Splitting torch, numpy, and requirements into separate `RUN` layers means that changes to `requirements.txt` do not invalidate the cached torch install (the slowest step at ~3 minutes).
