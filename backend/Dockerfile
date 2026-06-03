# ExplainPlan-Vision — Production Dockerfile
# Build : docker build -t explainplan-vision .
# Run   : docker run -p 8000:8000 -v $(pwd)/assets:/app/assets explainplan-vision
#
# Mount your Kaggle-downloaded assets:
#   assets/best_model.pth
#   assets/class_mappings.json

FROM python:3.11-slim

ARG DEBIAN_FRONTEND=noninteractive

# System libraries needed by OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
        libglib2.0-0 libgl1-mesa-glx libsm6 libxext6 libgomp1 curl \
    && rm -rf /var/lib/apt/lists/*

# Non-root user
RUN useradd --create-home appuser
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/

RUN mkdir -p assets logs/uploads && chown -R appuser:appuser /app
USER appuser

ENV EP_DEVICE=auto \
    EP_LOG_LEVEL=INFO \
    EP_CHECKPOINT_PATH=assets/best_model.pth \
    EP_CLASS_MAPPINGS_PATH=assets/class_mappings.json \
    PYTHONUNBUFFERED=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
