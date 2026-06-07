import clsx from "clsx";

export { clsx };

/** Format confidence as percentage string */
export const pct = (v) => `${(v * 100).toFixed(1)}%`;

/** Urgency → chip variant */
export const urgencyChip = (u = "") => {
  const l = u.toLowerCase();
  if (l === "critical") return "chip-red";
  if (l === "high")     return "chip-amber";
  if (l === "medium")   return "chip-cyan";
  return "chip-green";
};

/** Severity → chip variant */
export const severityChip = (s = "") => {
  const l = s.toLowerCase();
  if (l === "high")   return "chip-red";
  if (l === "medium") return "chip-amber";
  return "chip-green";
};

/** Trend arrow */
export const trendIcon = (t = "") => {
  if (t === "improving") return "↓";
  if (t === "worsening") return "↑";
  return "→";
};

/** base64 to src string */
export const b64src = (b64) =>
  b64 ? `data:image/png;base64,${b64}` : null;

/** Truncate long strings */
export const truncate = (str, n = 60) =>
  str && str.length > n ? str.slice(0, n) + "…" : str;
