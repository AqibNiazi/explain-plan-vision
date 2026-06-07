import React, { useState } from "react";
import { Shuffle } from "lucide-react";
import { urgencyChip } from "@/utils/helpers";
import clsx from "clsx";

export default function CounterfactualsCard({ counterfactuals }) {
  const [active, setActive] = useState(0);
  if (!counterfactuals?.length) return null;
  const cf = counterfactuals[active];

  return (
    <div className="panel p-6">
      <div className="flex items-center gap-2 mb-5">
        <div
          className="w-8 h-8 flex items-center justify-center"
          style={{ background: "rgba(0,229,255,0.1)", border: "1px solid var(--border-bright)" }}
        >
          <Shuffle size={15} style={{ color: "var(--accent-cyan)" }} />
        </div>
        <span className="font-mono text-xs uppercase tracking-widest" style={{ color: "var(--accent-cyan)" }}>
          Counterfactual Analysis
        </span>
      </div>

      {/* Scenario tabs */}
      <div className="flex flex-wrap gap-1 mb-5">
        {counterfactuals.map((c, i) => (
          <button
            key={i}
            onClick={() => setActive(i)}
            className={clsx(
              "font-mono text-xs px-3 py-1.5 transition-all",
              i === active
                ? "bg-[rgba(0,229,255,0.1)] border border-[var(--accent-cyan)] text-[var(--accent-cyan)]"
                : "border border-[var(--border-dim)] text-[var(--text-muted)] hover:text-[var(--text-primary)]"
            )}
          >
            {c.scenario}
          </button>
        ))}
      </div>

      {/* Active scenario */}
      <div className="mb-4">
        <p className="font-mono text-xs uppercase tracking-widest mb-2" style={{ color: "var(--text-muted)" }}>
          Scenario Description
        </p>
        <p className="text-sm mb-3" style={{ color: "var(--text-secondary)" }}>{cf.description}</p>
        <p className="text-sm" style={{ color: "var(--text-primary)" }}>{cf.narrative}</p>
      </div>

      {/* Delta comparison */}
      <div className="grid grid-cols-3 gap-3">
        <div className="p-3 text-center" style={{ background: "var(--bg-surface)", border: "1px solid var(--border-dim)" }}>
          <p className="font-mono text-xs mb-1" style={{ color: "var(--text-muted)" }}>Plan Delta</p>
          <p
            className="font-mono text-sm font-bold"
            style={{ color: cf.plan_delta > 0 ? "var(--accent-red)" : "var(--accent-green)" }}
          >
            {cf.plan_delta > 0 ? "+" : ""}{cf.plan_delta} steps
          </p>
        </div>
        <div className="p-3 text-center" style={{ background: "var(--bg-surface)", border: "1px solid var(--border-dim)" }}>
          <p className="font-mono text-xs mb-1" style={{ color: "var(--text-muted)" }}>Original Urgency</p>
          <span className={`chip ${urgencyChip(cf.original_urgency)}`}>{cf.original_urgency}</span>
        </div>
        <div className="p-3 text-center" style={{ background: "var(--bg-surface)", border: "1px solid var(--border-dim)" }}>
          <p className="font-mono text-xs mb-1" style={{ color: "var(--text-muted)" }}>CF Urgency</p>
          <span className={`chip ${urgencyChip(cf.cf_urgency)}`}>{cf.cf_urgency}</span>
        </div>
      </div>
    </div>
  );
}
