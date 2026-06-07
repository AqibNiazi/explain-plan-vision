import React, { useState } from "react";
import { Users } from "lucide-react";
import clsx from "clsx";

const personas = [
  { key: "farmer",     label: "Farmer",     color: "var(--accent-green)",  chip: "chip-green"  },
  { key: "agronomist", label: "Agronomist", color: "var(--accent-cyan)",   chip: "chip-cyan"   },
  { key: "researcher", label: "Researcher", color: "var(--accent-violet)", chip: "chip-violet" },
];

export default function ExplanationsCard({ explanations }) {
  const [active, setActive] = useState("farmer");
  if (!explanations) return null;

  const p = personas.find((x) => x.key === active);

  return (
    <div className="panel p-6">
      <div className="flex items-center gap-2 mb-5">
        <div
          className="w-8 h-8 flex items-center justify-center"
          style={{ background: "rgba(0,229,255,0.1)", border: "1px solid var(--border-bright)" }}
        >
          <Users size={15} style={{ color: "var(--accent-cyan)" }} />
        </div>
        <span className="font-mono text-xs uppercase tracking-widest" style={{ color: "var(--accent-cyan)" }}>
          Human-Adaptive Explanations
        </span>
      </div>

      {/* Persona tabs */}
      <div className="flex gap-2 mb-5">
        {personas.map((per) => (
          <button
            key={per.key}
            onClick={() => setActive(per.key)}
            className={clsx(
              "font-mono text-xs px-4 py-2 transition-all",
              active === per.key
                ? `bg-[rgba(0,229,255,0.1)] border border-[${per.color}]`
                : "border border-[var(--border-dim)] text-[var(--text-muted)]"
            )}
            style={active === per.key ? { borderColor: per.color, color: per.color } : {}}
          >
            {per.label}
          </button>
        ))}
      </div>

      {/* Explanation text */}
      <div
        className="p-4"
        style={{
          background: "var(--bg-surface)",
          borderLeft: `3px solid ${p.color}`,
          border: `1px solid var(--border-dim)`,
          borderLeft: `3px solid ${p.color}`,
        }}
      >
        <p className="text-sm leading-relaxed" style={{ color: "var(--text-primary)" }}>
          {explanations[active]}
        </p>
      </div>
    </div>
  );
}
