# ExplainPlan Vision — Frontend

React + Tailwind CSS 4 frontend for the ExplainPlan Vision neuro-symbolic plant disease analysis system.

## Quick Start

```bash
# 1. Install dependencies
npm install

# 2. Configure environment (copy and edit)
cp .env.example .env

# 3. Start dev server (auto-proxies /api/* → backend)
npm run dev
```

Open http://localhost:5173

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `""` (relative) | Backend base URL. Leave empty in dev (Vite proxy handles it). Set to `http://your-backend:8000` in production. |

## CORS / Proxy

In development the Vite dev server proxies all `/api/*` requests to `http://127.0.0.1:8000`, so no CORS configuration is needed.

In production, either:
- Set `VITE_API_URL` to the backend URL and ensure the FastAPI backend has your frontend origin in `CORS_ORIGINS`, or
- Serve the built frontend behind the same origin as the backend.

## Project Structure

```
src/
├── components/
│   ├── analysis/       # PredictionCard, XAICard, ReasoningCard, PlanCard, etc.
│   ├── layout/         # Navbar, Footer
│   └── ui/             # ImageUploader, reusable primitives
├── hooks/              # useAnalysis, useHealth
├── layout/             # AppLayout
├── pages/              # HomePage, AnalyzePage, MemoryPage, AboutPage
├── routes/             # AppRoutes
├── services/           # apiClient.js, analysisService.js
└── utils/              # helpers.js
```

## Key Endpoints Used

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/health` | GET | Model status + version |
| `/api/v1/full-analysis` | POST | Complete 10-stage pipeline |
| `/api/v1/memory` | GET | Temporal memory state |
| `/api/v1/memory` | DELETE | Clear memory |
| `/api/v1/knowledge-graph` | GET | KG metadata |

## Build for Production

```bash
npm run build
# Output in dist/
```
