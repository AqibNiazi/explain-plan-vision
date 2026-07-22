# Contributing to ExplainPlan Vision

Thank you for your interest in contributing. This document outlines the process for contributing code, research extensions, bug reports, and documentation improvements.

---

## Ways to Contribute

### Bug Reports
Open a GitHub Issue with:
- The endpoint or component that failed
- Request payload (sanitise any personal data)
- Full error message and stack trace
- HuggingFace Space build logs if it is a deployment issue

### Research Extensions
If you are extending the system for research (new XAI method, new reasoning rules, new plant classes), open an Issue first to discuss scope before opening a PR. This avoids duplicate effort.

### Documentation
Corrections to `docs/research_notes/` are always welcome — especially corrections to experimental findings or citations.

---

## Development Setup

```bash
# Clone
git clone https://github.com/AqibNiazi/ExplainPlan-Vision.git
cd ExplainPlan-Vision

# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install && npm run dev
```

---

## Code Style

**Python (backend):**
- Follow PEP 8
- Type hints on all public functions
- Docstrings on all classes and non-trivial functions
- No bare `except:` — always catch specific exceptions

**JavaScript (frontend):**
- Functional components only — no class components
- Custom hooks for all API state (`useAnalysis`, `useHealth`)
- No inline styles — use CSS variables from `index.css`

---

## Pull Request Process

1. Fork the repository
2. Create a branch: `git checkout -b feature/your-feature-name`
3. Make changes with descriptive commit messages
4. Test locally (backend + frontend)
5. Open a PR against `main` with:
   - Description of the change
   - Which research phase it belongs to (1–6)
   - Any relevant test results or accuracy numbers

---

## Research Contribution Guidelines

If your contribution includes new experimental results:

- Add a research note to `docs/research_notes/` following the existing format
- Include the metric, the dataset split it was measured on, and the measurement method
- Do not overwrite existing phase findings — add a new dated section

---

## Licence

By contributing, you agree that your contributions will be licensed under the MIT Licence.
