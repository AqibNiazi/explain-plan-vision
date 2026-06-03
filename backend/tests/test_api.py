"""
Pytest integration tests for all API endpoints.

Run all tests:
    pytest tests/ -v

Run only tests that do NOT require the model weights
(useful in CI where assets are not present):
    pytest tests/ -v -m "not requires_model"
"""

import io
from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient
from PIL import Image

ASSETS_PRESENT = (
    Path("assets/best_model.pth").exists()
    and Path("assets/class_mappings.json").exists()
)


def _make_jpeg(width: int = 224, height: int = 224) -> bytes:
    """Synthesise a green-tinted leaf image in memory."""
    rng = np.random.default_rng(42)
    arr = rng.integers(30, 180, (height, width, 3), dtype=np.uint8)
    arr[:, :, 1] = rng.integers(100, 255, (height, width), dtype=np.uint8)
    buf = io.BytesIO()
    Image.fromarray(arr, "RGB").save(buf, format="JPEG")
    buf.seek(0)
    return buf.read()


@pytest.fixture(scope="session")
def client():
    from backend.main import app
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


@pytest.fixture(scope="session")
def jpg():
    return _make_jpeg()


# ── Root and health ───────────────────────────────────────────────────────────

def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "docs" in r.json()


@pytest.mark.skipif(not ASSETS_PRESENT, reason="Model assets not in assets/")
def test_health_ok(client):
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    d = r.json()
    assert d["status"] == "ok"
    assert d["model_loaded"] is True
    assert d["num_classes"] > 0


# ── Knowledge graph ────────────────────────────────────────────────────────────

def test_knowledge_graph(client):
    r = client.get("/api/v1/knowledge-graph")
    assert r.status_code == 200
    d = r.json()
    assert d["num_nodes"] > 0
    assert d["num_edges"] > 0
    assert "disease" in d["node_types"]
    assert "treated_by" in d["edge_relations"]


# ── Input validation ───────────────────────────────────────────────────────────

def test_predict_no_file(client):
    r = client.post("/api/v1/predict")
    assert r.status_code == 422          # FastAPI unprocessable entity

def test_predict_bad_extension(client):
    r = client.post(
        "/api/v1/predict",
        files={"file": ("data.txt", b"not an image", "text/plain")},
    )
    assert r.status_code == 400

def test_predict_file_too_large(client):
    r = client.post(
        "/api/v1/predict",
        files={"file": ("big.jpg", b"x" * (11 * 1024 * 1024), "image/jpeg")},
    )
    assert r.status_code == 400

def test_predict_corrupt_image(client):
    r = client.post(
        "/api/v1/predict",
        files={"file": ("bad.jpg", b"\xff\xd8\xff" + b"\x00" * 100, "image/jpeg")},
    )
    # 400 or 422 — either is acceptable for a corrupt file
    assert r.status_code in (400, 422)


# ── Prediction ─────────────────────────────────────────────────────────────────

@pytest.mark.skipif(not ASSETS_PRESENT, reason="Model assets not in assets/")
@pytest.mark.requires_model
def test_predict_valid(client, jpg):
    r = client.post("/api/v1/predict",
                    files={"file": ("leaf.jpg", jpg, "image/jpeg")})
    assert r.status_code == 200
    d = r.json()
    assert 0.0 <= d["confidence"] <= 1.0
    assert d["severity"] in ("high", "medium", "low")
    assert isinstance(d["top3"], list)
    assert len(d["top3"]) > 0
    assert "image_b64" in d


# ── Explain ────────────────────────────────────────────────────────────────────

@pytest.mark.skipif(not ASSETS_PRESENT, reason="Model assets not in assets/")
@pytest.mark.requires_model
def test_explain_returns_images(client, jpg):
    r = client.post("/api/v1/explain",
                    files={"file": ("leaf.jpg", jpg, "image/jpeg")})
    assert r.status_code == 200
    d = r.json()
    assert len(d["gradcam_overlay_b64"]) > 100
    assert len(d["heatmap_b64"]) > 100
    assert d["infection_spread"] in ("localised", "moderate", "widespread")
    assert 0.0 <= d["focus_score"] <= 1.0


# ── Plan ───────────────────────────────────────────────────────────────────────

@pytest.mark.skipif(not ASSETS_PRESENT, reason="Model assets not in assets/")
@pytest.mark.requires_model
def test_plan_structure(client, jpg):
    r = client.post("/api/v1/plan",
                    files={"file": ("leaf.jpg", jpg, "image/jpeg")})
    assert r.status_code == 200
    d = r.json()
    assert len(d["actions"]) >= 1
    assert d["overall_urgency"] in ("critical", "high", "medium", "low", "none")
    for a in d["actions"]:
        assert "step" in a and "action" in a and "urgency" in a and "category" in a


# ── Full analysis ──────────────────────────────────────────────────────────────

@pytest.mark.skipif(not ASSETS_PRESENT, reason="Model assets not in assets/")
@pytest.mark.requires_model
def test_full_analysis_schema(client, jpg):
    r = client.post("/api/v1/full-analysis",
                    files={"file": ("leaf.jpg", jpg, "image/jpeg")})
    assert r.status_code == 200
    d = r.json()

    # Top-level keys
    for key in ["request_id", "processing_time_ms", "prediction", "xai",
                "reasoning", "plan", "counterfactuals", "decision_tree",
                "expected_urgency", "explanations", "trend"]:
        assert key in d, f"Missing key: {key}"

    # Prediction
    assert 0.0 <= d["prediction"]["confidence"] <= 1.0

    # XAI
    assert d["xai"]["infection_spread"] in ("localised", "moderate", "widespread")

    # Reasoning
    assert isinstance(d["reasoning"]["symbolic_facts"], list)
    assert d["reasoning"]["rules_fired"] >= 1

    # Plan
    assert len(d["plan"]["actions"]) >= 1

    # Counterfactuals
    assert len(d["counterfactuals"]) >= 1
    for cf in d["counterfactuals"]:
        assert {"scenario", "plan_delta", "narrative", "original_urgency", "cf_urgency"}.issubset(cf)

    # Explanations
    for mode in ("farmer", "agronomist", "researcher"):
        assert mode in d["explanations"]
        assert len(d["explanations"][mode]) > 50

    # Processing time
    assert d["processing_time_ms"] > 0


# ── Memory ─────────────────────────────────────────────────────────────────────

def test_clear_memory(client):
    r = client.delete("/api/v1/memory")
    assert r.status_code == 200
    assert r.json()["n_observations"] == 0


@pytest.mark.skipif(not ASSETS_PRESENT, reason="Model assets not in assets/")
@pytest.mark.requires_model
def test_memory_grows_after_analysis(client, jpg):
    client.delete("/api/v1/memory")
    client.post("/api/v1/full-analysis",
                files={"file": ("leaf.jpg", jpg, "image/jpeg")})
    r = client.get("/api/v1/memory")
    assert r.status_code == 200
    assert r.json()["n_observations"] >= 1
