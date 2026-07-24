# Phase 1 — Vision Foundation: Findings & Observations

**Date:** 2026  
**Author:** Muhammad Aqib Niazi  
**Platform:** Kaggle (GPU T4)  
**Dataset:** PlantVillage (~54,000 leaf images, 15 classes)


## Objective

Establish a reliable deep learning classifier for plant leaf disease that achieves sufficient accuracy to serve as the evidence base for downstream symbolic reasoning. The goal was not maximum accuracy in isolation, but accuracy *with calibrated confidence* the downstream reasoning engine requires reliable confidence values, not just correct top-1 predictions.

## Model Selection Rationale

**EfficientNet-B0** was selected over ResNet50, VGG16, and MobileNetV2 after evaluating four criteria:

| Criterion | EfficientNet-B0 | ResNet50 | Decision |
|---|---|---|---|
| Parameters | 5.3M | 25.6M | EfficientNet wins |
| CPU inference latency | ~180ms | ~310ms | EfficientNet wins |
| ImageNet Top-1 acc. | 77.1% | 76.1% | EfficientNet wins |
| GradCAM compatibility | ✅ Full | ✅ Full | Tie |

The parameter reduction from 25.6M → 5.3M was decisive for the deployment constraint: HuggingFace Spaces free tier has a 16GB RAM ceiling, and the full inference pipeline (vision + XAI + reasoning + planning) needed to fit comfortably.

**Transfer learning rationale:** ImageNet pre-training provides general visual features (edges, textures, colour gradients) that transfer well to leaf texture and disease lesion patterns, even though the domains differ significantly.


## Training Configuration

```python
model = efficientnet_b0(weights=EfficientNet_B0_Weights.IMAGENET1K_V1)
model.classifier[1] = nn.Linear(1280, 15)  # replace head

optimiser = Adam(model.parameters(), lr=1e-4)
scheduler = ReduceLROnPlateau(optimiser, patience=3, factor=0.5)
criterion = CrossEntropyLoss()
epochs = 25
batch_size = 32
```

**Augmentations applied:**
- RandomHorizontalFlip (p=0.5)
- RandomRotation(±15°)
- ColorJitter(brightness=0.2, contrast=0.2)

## Results

| Metric | Value |
|---|---|
| Top-1 Test Accuracy | **96.8%** |
| Top-3 Test Accuracy | **99.1%** |
| Best Validation Loss | 0.142 |
| Converged at Epoch | 18 |

### Per-Class F1 Scores

| Class | F1 Score | Notes |
|---|---|---|
| Tomato Late Blight | 0.978 | Highly distinctive brown lesions |
| Tomato Early Blight | 0.961 | Concentric ring pattern distinct |
| Tomato Leaf Mold | 0.943 | Occasionally confused with healthy |
| Tomato Bacterial Spot | 0.952 | |
| Potato Early Blight | 0.969 | |
| Potato Late Blight | 0.971 | |
| Corn Common Rust | 0.988 | Very distinctive orange pustules |
| Pepper Bacterial Spot | 0.934 | Lowest — overlaps with Tomato Bacterial Spot |
| Tomato Healthy | 0.981 | |
| *(remaining 6 classes)* | 0.940–0.975 | |

### Key Observations

**Observation 1 — Confidence calibration is asymmetric.** High-confidence predictions (>0.95) are almost always correct. Low-confidence predictions (0.60–0.80) show higher error rates, particularly on bacterial vs. fungal misclassifications. This motivated the downstream severity estimation heuristic: predictions below 0.85 are flagged with a confidence_note in the treatment plan.

**Observation 2 — Healthy-vs-diseased boundary is sharp.** The model rarely confuses healthy and diseased samples (only 3 healthy leaves misclassified as diseased across the entire test set). This is critical for the reasoning engine, where a false positive triggers unnecessary isolation and fungicide recommendations.

**Observation 3 — Within-species confusion exists.** Tomato Leaf Mold and Tomato Early Blight share overlapping visual features under certain lighting conditions. In these cases, the top-3 output captures both, and the counterfactual engine provides scenario analysis for the alternative diagnosis.

## Implications for Downstream Stages

- Confidence is used as a direct input to symbolic fact extraction (Stage 03). A confidence of 0.97 produces a `confidence_level(high)` fact; 0.72 would produce `confidence_level(medium)`.
- The `is_healthy` flag from Stage 01 bypasses the full reasoning pipeline if true — the system returns a wellness plan rather than a treatment plan.
- Top-3 alternatives are passed to the counterfactual engine to support the `early_detection` scenario.

## Files Produced

- `assets/best_model.pth` — EfficientNet-B0 weights (PyTorch)
- `assets/class_mappings.json` — index → disease class string mapping
- `notebooks/phase1_vision_foundation/` — full training notebook
