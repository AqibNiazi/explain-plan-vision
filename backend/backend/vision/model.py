"""EfficientNet-B0 inference engine. Architecture is identical to Phase 1."""

from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import torch
import torch.nn as nn
import timm
import albumentations as A
from albumentations.pytorch import ToTensorV2
from torch.amp import autocast
from loguru import logger

from backend.config import settings


class PlantDiseaseModel(nn.Module):
    """
    Phase 1 architecture — must not be modified.
    Weights load only if this matches the training-time definition exactly.
    """
    def __init__(self, model_name: str, num_classes: int,
                 embedding_dim: int = 512, dropout: float = 0.3):
        super().__init__()
        self.backbone   = timm.create_model(model_name, pretrained=False, num_classes=0)
        backbone_out    = self.backbone.num_features
        self.classifier = nn.Sequential(
            nn.Linear(backbone_out, embedding_dim),
            nn.BatchNorm1d(embedding_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(embedding_dim, num_classes),
        )

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        features = self.backbone(x)
        logits   = self.classifier(features)
        return logits, features


class VisionEngine:
    """Thread-safe singleton — one model loaded once, shared across all requests."""

    _instance: VisionEngine | None = None

    def __init__(self):
        self._load_mappings()
        self._load_model()
        self._build_transform()
        logger.info(
            f"VisionEngine ready | model={settings.model_name} "
            f"| classes={self.num_classes} | device={settings.device}"
        )

    @classmethod
    def get(cls) -> VisionEngine:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_mappings(self):
        path = Path(settings.class_mappings_path)
        if not path.exists():
            raise FileNotFoundError(
                f"class_mappings.json not found at '{path}'.\n"
                "Download it from your Phase 1 Kaggle output and put it in assets/."
            )
        with open(path) as f:
            m = json.load(f)
        self.class_to_idx : Dict[str, int] = m["class_to_idx"]
        self.idx_to_class : Dict[int, str] = {int(k): v for k, v in m["idx_to_class"].items()}
        self.classes      : list            = m["classes"]
        self.num_classes  : int             = m["num_classes"]

    def _load_model(self):
        ckpt = Path(settings.checkpoint_path)
        if not ckpt.exists():
            raise FileNotFoundError(
                f"best_model.pth not found at '{ckpt}'.\n"
                "Download it from your Phase 1 Kaggle output and put it in assets/."
            )
        self.model = PlantDiseaseModel(
            model_name    = settings.model_name,
            num_classes   = self.num_classes,
            embedding_dim = settings.embedding_dim,
            dropout       = settings.dropout,
        ).to(settings.device)
        state = torch.load(ckpt, map_location=settings.device, weights_only=True)
        self.model.load_state_dict(state)
        self.model.eval()
        logger.info(f"Checkpoint loaded from {ckpt}")

    def _build_transform(self):
        self.transform = A.Compose([
            A.Resize(settings.image_size, settings.image_size),
            A.Normalize(mean=settings.mean, std=settings.std),
            ToTensorV2(),
        ])

    def preprocess(self, image_rgb: np.ndarray) -> torch.Tensor:
        """Return a (1, 3, H, W) tensor on the configured device."""
        t = self.transform(image=image_rgb)["image"]
        return t.unsqueeze(0).to(settings.device)

    def preprocess_for_display(self, image_rgb: np.ndarray) -> np.ndarray:
        """Return a float32 (H, W, 3) in [0,1] for Grad-CAM overlay blending."""
        import cv2
        r = cv2.resize(image_rgb, (settings.image_size, settings.image_size))
        return r.astype(np.float32) / 255.0

    def predict(self, image_rgb: np.ndarray) -> dict:
        """Run inference and return a structured prediction dictionary."""
        tensor = self.preprocess(image_rgb)
        with torch.no_grad():
            with autocast("cuda", enabled=(settings.device == "cuda")):
                logits, features = self.model(tensor)
            probs = torch.softmax(logits.float(), dim=1)[0]

        top_idx    = probs.argmax().item()
        confidence = probs[top_idx].item()
        label      = self.idx_to_class[top_idx]
        plant, disease_type = self._parse_label(label)

        top3v, top3i = torch.topk(probs, k=min(3, self.num_classes))
        top3 = [
            {"disease_class": self.idx_to_class[i.item()], "confidence": round(v.item(), 4)}
            for v, i in zip(top3v, top3i)
        ]
        return {
            "disease"      : label,
            "plant"        : plant,
            "disease_type" : disease_type,
            "confidence"   : round(confidence, 4),
            "severity"     : self._severity(confidence),
            "top3"         : top3,
            "embedding"    : features[0].cpu().float().numpy(),
            "is_healthy"   : "healthy" in label.lower(),
        }

    @staticmethod
    def _parse_label(label: str) -> Tuple[str, str]:
        if "___" in label:
            p = label.split("___", 1)
            return p[0].replace("_", " ").strip(), p[1].replace("_", " ").strip()
        tk = label.split("_")
        return tk[0].strip(), " ".join(tk[1:]).strip()

    @staticmethod
    def _severity(conf: float) -> str:
        if conf >= settings.severity_high:   return "high"
        if conf >= settings.severity_medium: return "medium"
        return "low"
