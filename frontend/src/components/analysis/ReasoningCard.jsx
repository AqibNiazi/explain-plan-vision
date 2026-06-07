import React, { useState } from "react";
import { GitBranch, ChevronDown, ChevronUp } from "lucide-react";
import { urgencyChip } from "@/utils/helpers";

export default function ReasoningCard({ reasoning }) {
  const [showAll, setShowAll] = useState(false);
  if (!reasoning) return null;

  const {
    symbolic_facts, inferences, urgency_level, urgency_score,
    spread_risk, treatment_class, requires_isolation, rules_fired,
  } = reasoning;

  const visibleFacts = showAll ? symbolic_facts : symbolic_facts.slice(0, 5);

  return (
    <div className="panel p-6">
      {/* Header */}
      <div className="flex items-center gap-2 mb-5">
        <div
          className="w-8 h-8 flex items-center justify-center"
          style={{ background: "rgba(124,77,255,0.1)", border: "1px solid rgba(124,77,255,0.3)" }}
        >
          <GitBranch size={15} style={{ color: "var(--accent-violet)" }} />
        </div>
        <span className="font-mono text-xs uppercase tracking-widest" style={{ color: "var(--accent-violet)" }}>
          Symbolic Reasoning
        </span>
        <span className="ml-auto chip chip-violet">{rules_fired} rules fired</span>
      </div>

      {/* Key inferences */}
      <div className="grid grid-cols-2 gap-3 mb-5">
        <div className="p-3" style={{ background: "var(--bg-surface)", border: "1px solid var(--border-dim)" }}>
          <p className="font-mono text-xs mb-1" style={{ color: "var(--text-muted)" }}>Urgency Level</p>
          <span className={`chip ${urgencyChip(urgency_level)}`}>{urgency_level}</span>
        </div>
        <div className="p-3" style={{ background: "var(--bg-surface)", border: "1px solid var(--border-dim)" }}>
          <p className="font-mono text-xs mb-1" style={{ color: "var(--text-muted)" }}>Urgency Score</p>
          <p className="font-mono text-sm" style={{ color: "var(--accent-amber)" }}>
            {urgency_score?.toFixed(2)}
          </p>
        </div>
        <div className="p-3" style={{ background: "var(--bg-surface)", border: "1px solid var(--border-dim)" }}>
          <p className="font-mono text-xs mb-1" style={{ color: "var(--text-muted)" }}>Spread Risk</p>
          <p className="font-mono text-sm capitalize" style={{ color: "var(--text-primary)" }}>{spread_risk}</p>
        </div>
        <div className="p-3" style={{ background: "var(--bg-surface)", border: "1px solid var(--border-dim)" }}>
          <p className="font-mono text-xs mb-1" style={{ color: "var(--text-muted)" }}>Treatment Class</p>
          <p className="font-mono text-sm capitalize" style={{ color: "var(--text-primary)" }}>{treatment_class}</p>
        </div>
      </div>

      {requires_isolation && (
        <div
          className="flex items-center gap-2 px-3 py-2 mb-4 font-mono text-xs"
          style={{
            background: "rgba(255,64,96,0.06)",
            border: "1px solid rgba(255,64,96,0.3)",
            color: "var(--accent-red)",
          }}
        >
          ⚠ Isolation Required
        </div>
      )}

      {/* Symbolic facts */}
      <div>
        <p className="font-mono text-xs uppercase tracking-widest mb-3" style={{ color: "var(--text-muted)" }}>
          Symbolic Facts ({symbolic_facts.length})
        </p>
        <div className="flex flex-col gap-1.5">
          {visibleFacts.map((f, i) => (
            <div
              key={i}
              className="flex items-center gap-3 px-3 py-1.5"
              style={{ background: "var(--bg-surface)", borderLeft: "2px solid var(--accent-violet)" }}
            >
              <span className="font-mono text-xs" style={{ color: "var(--accent-violet)" }}>
                {f.predicate}
              </span>
              <span className="font-mono text-xs" style={{ color: "var(--text-secondary)" }}>
                ({f.arguments.join(", ")})
              </span>
              <span className="ml-auto font-mono text-xs" style={{ color: "var(--text-muted)" }}>
                {(f.confidence * 100).toFixed(0)}%
              </span>
            </div>
          ))}
        </div>
        {symbolic_facts.length > 5 && (
          <button
            onClick={() => setShowAll(!showAll)}
            className="flex items-center gap-1 mt-3 font-mono text-xs"
            style={{ color: "var(--accent-violet)" }}
          >
            {showAll ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
            {showAll ? "Show less" : `Show ${symbolic_facts.length - 5} more`}
          </button>
        )}
      </div>
    </div>
  );
}
