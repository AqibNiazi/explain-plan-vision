"""
ExplainPlan-Vision — FastAPI Application
==========================================
Start:   uvicorn backend.main:app --reload --port 8000
Docs:    http://localhost:8000/docs
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from backend.config import settings
from backend.api.routes import router
from backend.utils.logger import setup_logger

setup_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 60)
    logger.info(f"  {settings.app_name}  v{settings.app_version}")
    logger.info(f"  Device     : {settings.device}")
    logger.info(f"  Checkpoint : {settings.checkpoint_path}")
    logger.info("=" * 60)

    # Warm up all singletons at startup so the first API request
    # does not pay the model-loading cost.
    from backend.services.orchestrator import Orchestrator
    Orchestrator.get()

    logger.info("All engines loaded — server ready")
    yield
    logger.info("Server shutting down")


app = FastAPI(
    title       = settings.app_name,
    version     = settings.app_version,
    description = (
        "**ExplainPlan-Vision** — Explainable Neuro-Symbolic Visual Planning Agent\n\n"
        "Upload a leaf image to `/api/v1/full-analysis` and receive:\n\n"
        "- Disease prediction (EfficientNet-B0, 15 classes, PlantVillage)\n"
        "- Spatial explanation (Grad-CAM++ heatmap as base64 PNG)\n"
        "- Neuro-symbolic reasoning trace (20 inference rules + knowledge graph)\n"
        "- Dynamically adapted treatment plan (6 context mechanisms)\n"
        "- Counterfactual analysis (4 what-if scenarios)\n"
        "- Decision-tree look-ahead (probabilistic urgency estimate)\n"
        "- Human-adaptive explanations (farmer / agronomist / researcher)\n\n"
        "**Frontend**: Connect your React app to these endpoints. "
        "CORS is pre-configured for `localhost:3000` and `localhost:5173`."
    ),
    contact     = {"name": "ExplainPlan-Vision", "url": "https://github.com/your-username/ExplainPlan-Vision"},
    license_info= {"name": "MIT"},
    lifespan    = lifespan,
    docs_url    = "/docs",
    redoc_url   = "/redoc",
)

# CORS — allow the React dev server and production domain
app.add_middleware(
    CORSMiddleware,
    allow_origins     = settings.cors_origins,
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# Request timing header — useful for frontend performance monitoring
@app.middleware("http")
async def add_timing_header(request: Request, call_next):
    import time
    t0       = time.perf_counter()
    response = await call_next(request)
    ms       = round((time.perf_counter() - t0) * 1000, 1)
    response.headers["X-Process-Time-Ms"] = str(ms)
    logger.debug(f"{request.method} {request.url.path} → {response.status_code} ({ms} ms)")
    return response

# Global exception handler — returns clean JSON instead of HTML 500
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled error on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "error_type": type(exc).__name__},
    )

app.include_router(router, prefix=settings.api_prefix)

@app.get("/", include_in_schema=False)
def root():
    return {
        "name"   : settings.app_name,
        "version": settings.app_version,
        "docs"   : "/docs",
        "health" : f"{settings.api_prefix}/health",
    }
