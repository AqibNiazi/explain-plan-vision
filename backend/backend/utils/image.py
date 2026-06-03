"""Image loading, validation, and base64 utilities."""

import base64
import io
from pathlib import Path

import cv2
import numpy as np

from backend.config import settings


def load_image_rgb_from_bytes(data: bytes) -> np.ndarray:
    """Decode uploaded bytes into a uint8 RGB numpy array."""
    arr = np.frombuffer(data, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Cannot decode image — file may be corrupt or unsupported format.")
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def validate_upload(filename: str, size_bytes: int) -> None:
    """Raise ValueError if extension or file size is not acceptable."""
    suffix = Path(filename).suffix.lower()
    if suffix not in settings.allowed_extensions:
        raise ValueError(
            f"File type '{suffix}' is not allowed. "
            f"Accepted: {settings.allowed_extensions}"
        )
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if size_bytes > max_bytes:
        raise ValueError(
            f"File is too large ({size_bytes / 1_000_000:.1f} MB). "
            f"Maximum allowed: {settings.max_upload_mb} MB."
        )


def ndarray_to_b64(image_rgb: np.ndarray) -> str:
    """Encode a uint8 RGB array as a base64 PNG string."""
    bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
    _, buf = cv2.imencode(".png", bgr)
    return base64.b64encode(buf.tobytes()).decode()


def heatmap_to_b64(heatmap: np.ndarray) -> str:
    """Convert a float32 [0,1] heatmap to a jet-colourmap base64 PNG."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    coloured = (plt.cm.jet(np.clip(heatmap, 0, 1))[:, :, :3] * 255).astype(np.uint8)
    bgr = cv2.cvtColor(coloured, cv2.COLOR_RGB2BGR)
    _, buf = cv2.imencode(".png", bgr)
    return base64.b64encode(buf.tobytes()).decode()


def resize_rgb(image_rgb: np.ndarray, size: int = 224) -> np.ndarray:
    return cv2.resize(image_rgb, (size, size))
