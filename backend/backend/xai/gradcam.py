"""Grad-CAM++ spatial explanation engine."""

from __future__ import annotations
import numpy as np
import torch
import torch.nn as nn
from pytorch_grad_cam import GradCAMPlusPlus
from pytorch_grad_cam.utils.image import show_cam_on_image
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
from loguru import logger

from backend.config import settings
from backend.vision.model import VisionEngine


class _Wrapper(nn.Module):
    """
    pytorch-grad-cam expects model(x) → (batch, classes) tensor.
    Our model returns (logits, features), so this adapter is required.
    """
    def __init__(self, model: nn.Module):
        super().__init__()
        self.model = model

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        logits, _ = self.model(x)
        return logits


class GradCAMEngine:
    """Singleton Grad-CAM++ engine targeting EfficientNet-B0 backbone.conv_head."""

    _instance: GradCAMEngine | None = None

    def __init__(self, ve: VisionEngine):
        # Disable inplace activations — required for SHAP hooks (used in Phase 2 research)
        for m in ve.model.modules():
            if hasattr(m, "inplace"):
                m.inplace = False

        self.ve      = ve
        wrapped      = _Wrapper(ve.model).to(settings.device)
        wrapped.eval()
        self.cam = GradCAMPlusPlus(
            model=wrapped,
            target_layers=[wrapped.model.backbone.conv_head],
        )
        logger.info("GradCAMEngine ready | target=backbone.conv_head")

    @classmethod
    def get(cls) -> GradCAMEngine:
        if cls._instance is None:
            cls._instance = cls(VisionEngine.get())
        return cls._instance

    def generate(
        self,
        image_rgb        : np.ndarray,
        target_class_idx : int | None = None,
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Returns
        -------
        heatmap  : float32 (H, W) in [0, 1]
        overlay  : uint8  (H, W, 3) — heatmap blended onto the input image
        """
        tensor    = self.ve.preprocess(image_rgb)
        display   = self.ve.preprocess_for_display(image_rgb)
        targets   = [ClassifierOutputTarget(target_class_idx)] if target_class_idx is not None else None
        heatmap   = self.cam(input_tensor=tensor, targets=targets)[0]
        overlay   = show_cam_on_image(display, heatmap, use_rgb=True)
        return heatmap, overlay

    def spatial_stats(self, heatmap: np.ndarray) -> dict:
        """Compute focus score, entropy, and spread label from the heatmap."""
        focus   = float((heatmap >= np.percentile(heatmap, 80)).mean())
        spread  = "localised" if focus < 0.06 else "moderate" if focus < 0.15 else "widespread"
        h       = heatmap.flatten() + 1e-8
        h      /= h.sum()
        entropy = float(-np.sum(h * np.log(h)))
        return {
            "focus_score"       : round(focus,   4),
            "activation_entropy": round(entropy, 4),
            "infection_spread"  : spread,
        }
