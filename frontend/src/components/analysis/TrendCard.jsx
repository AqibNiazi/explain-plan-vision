import React from "react";
import { Clock, TrendingUp, TrendingDown, Minus } from "lucide-react";
import { trendIcon } from "@/utils/helpers";

const TrendRow = ({ label, value }) => {
  const icon =
    value === "improving" ? <TrendingDown size={13} style={{ color: "var(--accent-green)" }} /> :
    value === "worsening" ? <TrendingUp   size={13} style={{ color: "var(--accent-red)" }} /> :
    <Minus size={13} style={{ color: "var(--text-muted)" }} />;

  const color =
    value === "improving" ? "var(--accent-green)" :
    value === "worsening" ? "var(--accent-red)"   :
    "var(--text-secondary)";

  return (
    <div className="flex items-center justify-between py-2" style={{ borderBottom: "1px solid var(--border-dim)" }}>
      <span className="font-mono text-xs" style={{ color: "var(--text-muted)" }}>{label}</span>
      <div className="flex items-center gap-2">
        {icon}
        <span className="font-mono text-xs capitalize" style={{ color }}>{value}</span>
      </div>
    </div>
  );
};

export default function TrendCard({ trend }) {
  if (!trend) return null;
  const { severity_trend, urgency_trend, spread_trend, disease_stable,
          n_observations, latest_urgency, latest_severity, summary } = trend;

  return (
    <div className="panel p-6">
      <div className="flex items-center gap-2 mb-5">
        <div
          className="w-8 h-8 flex items-center justify-center"
          style={{ background: "rgba(0,255,157,0.1)", border: "1px solid rgba(0,255,157,0.3)" }}
        >
          <Clock size={15} style={{ color: "var(--accent-green)" }} />
        </div>
        <span className="font-mono text-xs uppercase tracking-widest" style={{ color: "var(--accent-green)" }}>
          Temporal Trend
        </span>
        <span className="ml-auto chip chip-cyan">{n_observations} obs.</span>
      </div>

      {summary && (
        <div
          className="px-3 py-2 mb-4 font-mono text-xs"
          style={{ background: "var(--bg-surface)", borderLeft: "2px solid var(--accent-green)", color: "var(--text-secondary)" }}
        >
          {summary}
        </div>
      )}

      <TrendRow label="Severity Trend"  value={severity_trend} />
      <TrendRow label="Urgency Trend"   value={urgency_trend}  />
      <TrendRow label="Spread Trend"    value={spread_trend}   />

      <div className="flex gap-3 mt-3">
        <div className="flex-1 p-3 text-center" style={{ background: "var(--bg-surface)", border: "1px solid var(--border-dim)" }}>
          <p className="font-mono text-xs mb-1" style={{ color: "var(--text-muted)" }}>Latest Urgency</p>
          <p className="font-mono text-xs capitalize" style={{ color: "var(--text-primary)" }}>{latest_urgency}</p>
        </div>
        <div className="flex-1 p-3 text-center" style={{ background: "var(--bg-surface)", border: "1px solid var(--border-dim)" }}>
          <p className="font-mono text-xs mb-1" style={{ color: "var(--text-muted)" }}>Disease Stable</p>
          <p className="font-mono text-xs" style={{ color: disease_stable ? "var(--accent-green)" : "var(--accent-red)" }}>
            {disease_stable ? "Stable" : "Unstable"}
          </p>
        </div>
      </div>
    </div>
  );
}
