import axios from "axios";

// ── Base URL ──────────────────────────────────────────────────────────────────
// Vite proxy forwards /api/* → backend, so in dev we can use relative paths.
// In production set VITE_API_URL to point at the deployed backend.
const serverBaseURL = import.meta.env.VITE_API_URL || "";

const clientBaseURL = axios.create({
  baseURL: serverBaseURL,
  timeout: 60000, // 60s — full-analysis with GradCAM can be slow on CPU
  headers: { "Content-Type": "application/json" },
});

// ── API Base Paths ────────────────────────────────────────────────────────────
const apiBasePath = "/api/v1";

// ── Endpoint Definitions ─────────────────────────────────────────────────────
const clientEndPoints = {
  // System
  health:         `${apiBasePath}/health`,
  knowledgeGraph: `${apiBasePath}/knowledge-graph`,

  // Analysis
  predict:        `${apiBasePath}/predict`,
  explain:        `${apiBasePath}/explain`,
  plan:           `${apiBasePath}/plan`,
  fullAnalysis:   `${apiBasePath}/full-analysis`,

  // Memory
  memory:         `${apiBasePath}/memory`,
  clearMemory:    `${apiBasePath}/memory`,
};

export { clientBaseURL, clientEndPoints };
