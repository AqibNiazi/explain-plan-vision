"""
Centralised configuration.
Every value can be overridden with an EP_* environment variable or a .env file.
"""

from __future__ import annotations
from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # Application
    app_name: str    = "ExplainPlan-Vision"
    app_version: str = "1.0.0"
    debug: bool      = False

    # Model assets
    checkpoint_path     : str = "assets/best_model.pth"
    class_mappings_path : str = "assets/class_mappings.json"
    model_name          : str = "efficientnet_b0"
    embedding_dim       : int = 512
    dropout             : float = 0.3
    image_size          : int = 224
    mean                : List[float] = [0.485, 0.456, 0.406]
    std                 : List[float] = [0.229, 0.224, 0.225]

    # Hardware
    device: str = "auto"          # auto | cuda | cpu

    # Inference thresholds
    severity_high   : float = 0.85
    severity_medium : float = 0.60
    confidence_gate : float = 0.60   # below this → add verification step

    # Reasoning
    inference_depth  : int = 3
    lookahead_steps  : int = 4
    memory_capacity  : int = 20

    # API
    api_prefix   : str        = "/api/v1"
    cors_origins : List[str]  = ["http://localhost:3000", "http://localhost:5173"]
    log_level    : str        = "INFO"
    log_file     : str        = "logs/app.log"

    # File uploads
    upload_dir         : str       = "logs/uploads"
    max_upload_mb      : int       = 10
    allowed_extensions : List[str] = [".jpg", ".jpeg", ".png", ".webp"]

    model_config = {"env_prefix": "EP_", "case_sensitive": False}


settings = Settings()

# Resolve device
import torch
if settings.device == "auto":
    settings.device = "cuda" if torch.cuda.is_available() else "cpu"

# Ensure runtime directories exist
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
Path("logs").mkdir(exist_ok=True)
