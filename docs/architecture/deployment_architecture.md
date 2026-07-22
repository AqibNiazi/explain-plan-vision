# Deployment Architecture — ExplainPlan Vision

## Overview

```
Developer pushes to GitHub
        │
        ├─► Vercel (Frontend)
        │       ├── npm run build → dist/
        │       ├── Static files on Vercel CDN / Edge Network
        │       └── VITE_API_URL → HuggingFace Spaces
        │
        └─► HuggingFace Spaces (Backend)
                ├── Docker build triggered on git push
                ├── python:3.11-slim base
                ├── Port 7860 (HF requirement)
                └── uvicorn backend.main:app --port 7860
```

---

## Frontend — Vercel

### Stack
- React 19 + Tailwind CSS 4 + Vite 7
- Build output: `frontend/dist/` (static HTML/JS/CSS)
- Deployed as static site on Vercel Edge Network

### Build Configuration

```bash
# Build command
npm run build

# Output directory
dist/

# Environment variable (set in Vercel dashboard)
VITE_API_URL=https://aqibniazi-explainplan-vision-api.hf.space
```

### Dev vs Production Routing

In development, Vite proxy forwards `/api/*` to localhost:8000 — no CORS configuration needed:

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

In production, Axios calls go directly to `VITE_API_URL` (the HuggingFace Space URL), so CORS must be configured on the backend.

---

## Backend — HuggingFace Spaces (Docker)

### Space Configuration (README.md header)

```yaml
---
title: Explainplan Vision Api
emoji: 🌿
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
license: mit
---
```

### Dockerfile Strategy

Three-step pip install order prevents dependency conflicts:

```dockerfile
# Step 1 — numpy pinned before torch touches it
RUN pip install numpy==1.26.4

# Step 2 — torch CPU-only wheel (~180MB vs 2.4GB CUDA)
RUN pip install torch==2.2.2+cpu torchvision==0.17.2+cpu \
    --extra-index-url https://download.pytorch.org/whl/cpu

# Step 3 — all other dependencies
RUN pip install -r requirements.txt
```

**Why this order matters:**
- numpy must be pinned to 1.26.4 — numpy 2.x breaks torch 2.2's ABI expectations
- torch CPU wheel must install before `timm`, `grad-cam`, `albumentations` — otherwise pip may pull the CUDA wheel (2.4GB) when resolving transitive deps
- `gcc`, `g++`, `python3-dev` in apt — required by `stringzilla` (albumentations dep) which compiles from source

### Model Weights Strategy

`best_model.pth` and `class_mappings.json` are committed directly to the Space repository under `assets/` and copied into the Docker image at build time:

```dockerfile
COPY --chown=user assets/ ./assets/
```

**Alternative (for large models):** Use `startup.py` to download from HuggingFace Model Hub at container startup. The `startup.py` script is included in the repo and called from `backend/main.py` before engine initialisation.

### Container Resource Usage

| Resource | Value |
|---|---|
| RAM at idle | ~1.2 GB |
| RAM during inference | ~1.6 GB |
| HF Spaces free tier RAM | 16 GB |
| Disk (model + deps) | ~2.8 GB |
| CPU inference latency | ~2.1s / request |
| Cold start time | ~45s |
| Sleep after inactivity | 48 hours |

### CORS Configuration

```python
# backend/config.py
cors_origins: List[str] = [
    "http://localhost:5173",       # Vite dev server
    "http://localhost:3000",       # Alt dev port
    "https://your-app.vercel.app", # Production frontend ← update this
]
```

**Important:** Remove `"*"` from cors_origins in production. Wildcard CORS on a public API is a security risk.

---

## CI/CD Flow

```
git push origin main (GitHub)
        │
        ├─► Vercel detects push → runs npm run build → deploys dist/
        │   (Build time: ~60s)
        │
        └─► HuggingFace Spaces detects push → runs Docker build → deploys
            (Build time: ~8–12 min due to torch install)
```

No manual deployment steps after initial setup.

---

## Environment Variables Reference

| Variable | Where Set | Value (Production) |
|---|---|---|
| `VITE_API_URL` | Vercel dashboard | `https://aqibniazi-explainplan-vision-api.hf.space` |
| `EP_DEVICE` | Dockerfile ENV | `cpu` |
| `EP_CHECKPOINT_PATH` | Dockerfile ENV | `assets/best_model.pth` |
| `EP_CLASS_MAPPINGS_PATH` | Dockerfile ENV | `assets/class_mappings.json` |
| `EP_LOG_LEVEL` | Dockerfile ENV | `INFO` |
| `HF_MODEL_REPO` | HF Space secrets (optional) | `aqibniazi/explainplan-vision-weights` |

---

## Known Deployment Constraints

| Constraint | Impact | Mitigation |
|---|---|---|
| HF Spaces free tier sleeps after 48h inactivity | First request after sleep: ~60s | Acceptable for demo/research use |
| CPU-only inference | ~2.1s per request (vs ~0.3s GPU) | EfficientNet-B0 chosen for small param count |
| numpy 1.26.4 pin | Prevents numpy 2.x features | Not needed for this pipeline |
| 1 uvicorn worker | No parallel request handling | Sufficient for demo load |
| Model in Docker image | ~20MB added to image size | Simpler than runtime download |
