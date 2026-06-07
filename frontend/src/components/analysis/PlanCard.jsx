import React from "react";
import { Layers, AlertOctagon, Clock } from "lucide-react";
import { urgencyChip } from "@/utils/helpers";

const categoryColor = {
  containment:  "var(--accent-red)",
  chemical:     "var(--accent-amber)",
  physical:     "var(--accent-cyan)",
  environmental:"var(--accent-green)",
  monitoring:   "var(--accent-violet)",
  verification: "var(--text-secondary)",
};

export default function PlanCard({ plan }) {
  if (!plan) return null;
  const { disease_type, overall_urgency, actions, adaptations, escalation_flag,
          confidence_note, monitoring_interval, inference_trace } = plan;

  return (
    <div className="panel p-6">
      {/* Header */}
      <div className="flex items-center gap-2 mb-5">
        <div
          className="w-8 h-8 flex items-center justify-center"
          style={{ background: "rgba(255,179,0,0.1)", border: "1px solid rgba(255,179,0,0.3)" }}
        >
          <Layers size={15} style={{ color: "var(--accent-amber)" }} />
        </div>
        <span className="font-mono text-xs uppercase tracking-widest" style={{ color: "var(--accent-amber)" }}>
          Treatment Plan
        </span>
        <span className={`ml-auto chip ${urgencyChip(overall_urgency)}`}>{overall_urgency} urgency</span>
      </div>

      {/* Meta */}
      <div className="flex flex-wrap gap-3 mb-5">
        <div className="flex items-center gap-2 font-mono text-xs" style={{ color: "var(--text-secondary)" }}>
          <Clock size={12} />
          Monitoring: {monitoring_interval}
        </div>
        {escalation_flag && (
          <div className="flex items-center gap-2 font-mono text-xs" style={{ color: "var(--accent-red)" }}>
            <AlertOctagon size={12} />
            Escalation Required
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="flex flex-col gap-2 mb-5">
        {actions.map((a) => {
          const col = categoryColor[a.category] || "var(--text-secondary)";
          return (
            <div
              key={a.step}
              className="flex items-start gap-3 p-3"
              style={{ background: "var(--bg-surface)", border: "1px solid var(--border-dim)", borderLeft: `3px solid ${col}` }}
            >
              <span className="font-mono text-xs w-6 shrink-0 pt-0.5" style={{ color: "var(--text-muted)" }}>
                {String(a.step).padStart(2, "0")}
              </span>
              <div className="flex-1">
                <p className="text-sm mb-1" style={{ color: "var(--text-primary)" }}>{a.action}</p>
                <div className="flex gap-2">
                  <span className="font-mono text-xs capitalize" style={{ color: col }}>{a.category}</span>
                  <span className={`chip ${urgencyChip(a.urgency)}`} style={{ fontSize: 10 }}>{a.urgency}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Confidence note */}
      {confidence_note && (
        <div
          className="px-3 py-2 font-mono text-xs mb-4"
          style={{ background: "var(--bg-surface)", borderLeft: "2px solid var(--accent-amber)", color: "var(--text-secondary)" }}
        >
          {confidence_note}
        </div>
      )}

      {/* Adaptations */}
      {adaptations?.length > 0 && (
        <div>
          <p className="font-mono text-xs uppercase tracking-widest mb-2" style={{ color: "var(--text-muted)" }}>
            Plan Adaptations ({adaptations.length})
          </p>
          {adaptations.map((ad, i) => (
            <div key={i} className="font-mono text-xs py-1" style={{ color: "var(--text-secondary)", borderBottom: "1px solid var(--border-dim)" }}>
              {ad.reason || ad.description || JSON.stringify(ad)}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
