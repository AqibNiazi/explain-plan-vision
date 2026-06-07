import React from "react";
import { Leaf, AlertTriangle, CheckCircle } from "lucide-react";
import { pct, severityChip, urgencyChip } from "@/utils/helpers";

export default function PredictionCard({ prediction }) {
  if (!prediction) return null;
  const { disease, plant, disease_type, confidence, severity, is_healthy, top3 } = prediction;

  return (
    <div className="panel p-6">
      {/* Header */}
      <div className="flex items-center gap-2 mb-5">
        <div
          className="w-8 h-8 flex items-center justify-center"
          style={{ background: "rgba(0,229,255,0.1)", border: "1px solid var(--border-bright)" }}
        >
          <Leaf size={15} style={{ color: "var(--accent-cyan)" }} />
        </div>
        <span className="font-mono text-xs uppercase tracking-widest" style={{ color: "var(--accent-cyan)" }}>
          Classification Result
        </span>
      </div>

      {/* Primary result */}
      <div className="mb-5">
        <div className="flex items-start gap-3 mb-3">
          {is_healthy ? (
            <CheckCircle size={18} style={{ color: "var(--accent-green)", marginTop: 3 }} />
          ) : (
            <AlertTriangle size={18} style={{ color: "var(--accent-amber)", marginTop: 3 }} />
          )}
          <div>
            <p
              className="font-display font-bold text-xl leading-tight"
              style={{ color: "var(--text-primary)", fontFamily: "var(--font-display)" }}
            >
              {disease}
            </p>
            <p className="font-mono text-xs mt-1" style={{ color: "var(--text-secondary)" }}>
              {plant} · {disease_type}
            </p>
          </div>
        </div>

        {/* Confidence bar */}
        <div className="mt-4">
          <div className="flex justify-between mb-1">
            <span className="font-mono text-xs" style={{ color: "var(--text-muted)" }}>Confidence</span>
            <span className="font-mono text-xs" style={{ color: "var(--accent-cyan)" }}>{pct(confidence)}</span>
          </div>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: pct(confidence) }} />
          </div>
        </div>
      </div>

      {/* Chips */}
      <div className="flex flex-wrap gap-2 mb-5">
        <span className={`chip ${severityChip(severity)}`}>Severity: {severity}</span>
        {is_healthy && <span className="chip chip-green">Healthy</span>}
      </div>

      {/* Top 3 */}
      <div>
        <p className="font-mono text-xs uppercase tracking-widest mb-3" style={{ color: "var(--text-muted)" }}>
          Top-3 Alternatives
        </p>
        <div className="flex flex-col gap-2">
          {top3.map((t, i) => (
            <div key={t.disease_class} className="flex items-center gap-3">
              <span className="font-mono text-xs w-5 text-right" style={{ color: "var(--text-muted)" }}>
                {i + 1}.
              </span>
              <div className="flex-1">
                <div className="flex justify-between mb-0.5">
                  <span className="font-mono text-xs" style={{ color: "var(--text-secondary)" }}>
                    {t.disease_class}
                  </span>
                  <span className="font-mono text-xs" style={{ color: "var(--text-muted)" }}>
                    {pct(t.confidence)}
                  </span>
                </div>
                <div className="progress-bar" style={{ height: 2 }}>
                  <div
                    className="progress-fill"
                    style={{
                      width: pct(t.confidence),
                      background: i === 0
                        ? "linear-gradient(90deg, var(--accent-cyan), var(--accent-green))"
                        : "var(--border-bright)",
                      boxShadow: "none",
                    }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
