# Research Notes — ExplainPlan Vision

These notes document findings, observations, and decisions made during each development phase. They are written to serve two purposes:

1. **Reproducibility** — another researcher can understand what was tried, what worked, and what the numbers actually are.
2. **Paper scaffolding** — when writing a conference or journal submission, these notes provide the raw material for the Methods, Results, and Discussion sections.

---

## Index

| File | Phase | Key Numbers |
|---|---|---|
| `phase1_findings.md` | Vision Foundation | Top-1: 96.8%, Top-3: 99.1%, 5.3M params |
| `phase2_xai_results.md` | Explainability | Grad-CAM++ vs LIME vs SHAP comparison, r=0.74 focus/confidence correlation |
| `phase3_phase4_results.md` | Planning + Reasoning | Counterfactual plan_delta, rules_fired correlation r=0.81 |
| `phase5_deployment_notes.md` | Deployment | Docker errors fixed, latency: ~2.1s/req, RAM: ~1.2GB |
| `future_work.md` | Phase 6 Plan | LLM grounding design, evaluation metrics, timeline |

---

## How to Use These Notes

### For a Technical Report or Thesis

The findings in `phase2_xai_results.md` (Observation 3 — focus_score/confidence correlation) and `phase3_phase4_results.md` (counterfactual plan_delta analysis) are the most academically interesting results. Lead with those in an abstract.

### For a PhD Application Portfolio

The architecture in `phase3_phase4_results.md` — the grounding pipeline and end-to-end traceability — is the research contribution that differentiates this project from a standard classification paper. Frame it as: *"I designed a grounding pipeline that converts continuous neural outputs into verifiable symbolic facts, enabling full traceability from pixel to treatment step."*

### For a Supervisor Meeting

Bring `future_work.md`. The reasoning alignment evaluation in Module 6.4 is a concrete, scoped research question with a clear methodology and a plausible publishable result.

---

## Adding New Notes

When adding a new research note:

1. Name it `phaseN_description.md`
2. Include: objective, methodology, key numerical results, observations, limitations, implications for downstream stages
3. Do not delete or overwrite existing observations — add a new dated section if updating
4. Add it to the index table above
