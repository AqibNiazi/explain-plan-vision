import { clientBaseURL, clientEndPoints } from "./apiClient";

// ── Helpers ───────────────────────────────────────────────────────────────────
const toFormData = (file) => {
  const fd = new FormData();
  fd.append("file", file);
  return fd;
};

const multipartConfig = {
  headers: { "Content-Type": "multipart/form-data" },
  timeout: 90000,
};

// ── Health ────────────────────────────────────────────────────────────────────
export const fetchHealth = async () => {
  const { data } = await clientBaseURL.get(clientEndPoints.health);
  return data;
};

// ── Full Analysis (primary endpoint) ─────────────────────────────────────────
export const runFullAnalysis = async (file, onUploadProgress) => {
  const { data } = await clientBaseURL.post(
    clientEndPoints.fullAnalysis,
    toFormData(file),
    {
      ...multipartConfig,
      onUploadProgress,
    }
  );
  return data;
};

// ── Predict only ─────────────────────────────────────────────────────────────
export const runPredict = async (file) => {
  const { data } = await clientBaseURL.post(
    clientEndPoints.predict,
    toFormData(file),
    multipartConfig
  );
  return data;
};

// ── Explain only (Grad-CAM) ───────────────────────────────────────────────────
export const runExplain = async (file) => {
  const { data } = await clientBaseURL.post(
    clientEndPoints.explain,
    toFormData(file),
    multipartConfig
  );
  return data;
};

// ── Plan only ─────────────────────────────────────────────────────────────────
export const runPlan = async (file) => {
  const { data } = await clientBaseURL.post(
    clientEndPoints.plan,
    toFormData(file),
    multipartConfig
  );
  return data;
};

// ── Memory ────────────────────────────────────────────────────────────────────
export const fetchMemory = async () => {
  const { data } = await clientBaseURL.get(clientEndPoints.memory);
  return data;
};

export const clearMemory = async () => {
  const { data } = await clientBaseURL.delete(clientEndPoints.clearMemory);
  return data;
};

// ── Knowledge Graph ───────────────────────────────────────────────────────────
export const fetchKnowledgeGraph = async () => {
  const { data } = await clientBaseURL.get(clientEndPoints.knowledgeGraph);
  return data;
};
