import React, { useState } from "react";
import { Eye, Thermometer } from "lucide-react";
import { b64src, pct } from "@/utils/helpers";

export default function XAICard({ xai, imageSrc }) {
  const [view, setView] = useState("overlay"); // overlay | heatmap | original

  if (!xai) return null;
  const { gradcam_overlay_b64, heatmap_b64, infection_spread, focus_score, activation_entropy } = xai;

  const tabs = [
    { id: "overlay",  label: "GradCAM Overlay" },
    { id: "heatmap",  label: "Raw Heatmap"     },
    { id: "original", label: "Original"        },
  ];

  const imgSrc =
    view === "overlay"  ? b64src(gradcam_overlay_b64) :
    view === "heatmap"  ? b64src(heatmap_b64) :
    imageSrc;

  const spreadColor = {
    localised:   "var(--accent-green)",
    moderate:    "var(--accent-amber)",
    widespread:  "var(--accent-red)",
  }[infection_spread] || "var(--text-secondary)";

  return (
    <div className="panel p-6">
      {/* Header */}
      <div className="flex items-center gap-2 mb-5">
        <div
          className="w-8 h-8 flex items-center justify-center"
          style={{ background: "rgba(0,255,157,0.1)", border: "1px solid rgba(0,255,157,0.3)" }}
        >
          <Eye size={15} style={{ color: "var(--accent-green)" }} />
        </div>
        <span className="font-mono text-xs uppercase tracking-widest" style={{ color: "var(--accent-green)" }}>
          Grad-CAM++ Explanation
        </span>
      </div>

      {/* Tab switcher */}
      <div className="flex gap-1 mb-4" style={{ borderBottom: "1px solid var(--border-dim)" }}>
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setView(t.id)}
            className={`font-mono text-xs px-3 py-2 transition-all ${
              view === t.id ? "tab-active" : "tab-inactive hover:text-[var(--text-primary)]"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Image */}
      <div
        className="flex items-center justify-center mb-5"
        style={{ background: "var(--bg-root)", minHeight: 200, border: "1px solid var(--border-dim)" }}
      >
        {imgSrc ? (
          <img
            src={imgSrc}
            alt={view}
            className="max-h-64 max-w-full object-contain"
          />
        ) : (
          <span className="font-mono text-xs" style={{ color: "var(--text-muted)" }}>
            No image available
          </span>
        )}
      </div>

      {/* Spatial stats */}
      <div className="grid grid-cols-3 gap-3">
        <div
          className="p-3 text-center"
          style={{ background: "var(--bg-surface)", border: "1px solid var(--border-dim)" }}
        >
          <p className="font-mono text-xs mb-1" style={{ color: "var(--text-muted)" }}>Spread</p>
          <p className="font-mono text-sm font-bold capitalize" style={{ color: spreadColor }}>
            {infection_spread}
          </p>
        </div>
        <div
          className="p-3 text-center"
          style={{ background: "var(--bg-surface)", border: "1px solid var(--border-dim)" }}
        >
          <p className="font-mono text-xs mb-1" style={{ color: "var(--text-muted)" }}>Focus</p>
          <p className="font-mono text-sm font-bold" style={{ color: "var(--accent-cyan)" }}>
            {focus_score?.toFixed(3)}
          </p>
        </div>
        <div
          className="p-3 text-center"
          style={{ background: "var(--bg-surface)", border: "1px solid var(--border-dim)" }}
        >
          <p className="font-mono text-xs mb-1" style={{ color: "var(--text-muted)" }}>Entropy</p>
          <p className="font-mono text-sm font-bold" style={{ color: "var(--accent-violet)" }}>
            {activation_entropy?.toFixed(3)}
          </p>
        </div>
      </div>
    </div>
  );
}
