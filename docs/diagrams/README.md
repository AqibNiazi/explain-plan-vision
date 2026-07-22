# Diagrams — ExplainPlan Vision

All diagrams are SVG format — open directly in any browser or embed in Markdown with `![](path/to/file.svg)`.

---

## `system_architecture.svg`

The primary architecture diagram. Shows all 10 pipeline stages vertically from input to unified response, with data artifacts on the right and the temporal memory branch. Use this diagram in presentations and the README.

**Best for:** Project overview, README header, conference poster.

---

## `pipeline_flow.svg`

Full inference pipeline with data artifacts flowing out of each stage in the middle column, and parallel stages 07+08 (counterfactuals + decision tree) in the right column. More detailed than the system architecture diagram.

**Best for:** Technical documentation, thesis figures, supervisor meetings.

---

## `reasoning_pipeline.svg`

Focused diagram of the neuro-symbolic reasoning layer (Stages 03–04). Shows the neural inputs at the top, symbolic fact extraction in the middle, knowledge graph inference rules and derived inferences below, and the three downstream consumers (planner, counterfactuals, explanations) at the bottom.

**Best for:** Explaining the grounding pipeline to an AI / XAI audience.

---

## `deployment_architecture.svg`

Shows the two-service deployment: Vercel (React SPA) on the left, HuggingFace Spaces Docker container on the right, with the HTTPS REST connection between them, environment variable configuration, and the internal container structure (Uvicorn → FastAPI → inference pipeline).

**Best for:** DevOps documentation, deployment guides, system administration context.

---

## How to Embed in README

```markdown
## Architecture

![System Architecture](docs/diagrams/system_architecture.svg)

## Inference Pipeline

![Pipeline Flow](docs/diagrams/pipeline_flow.svg)
```

## How to Export to PNG (for submissions that don't accept SVG)

```bash
# Using Inkscape (recommended)
inkscape --export-type=png --export-dpi=300 system_architecture.svg

# Using ImageMagick
convert -density 300 system_architecture.svg system_architecture.png

# Using Node.js (svg2png)
npx svg2png system_architecture.svg --output=system_architecture.png --width=1800
```
