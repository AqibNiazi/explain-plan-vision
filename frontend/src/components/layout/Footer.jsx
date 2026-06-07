import React from "react";
import { FlaskConical, Github } from "lucide-react";

export default function Footer() {
  return (
    <footer className="relative z-10 border-t border-[var(--border-dim)] mt-auto">
      <div className="max-w-7xl mx-auto px-6 py-6 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <FlaskConical size={14} className="text-[var(--accent-cyan)] opacity-60" />
          <span className="font-mono text-xs text-[var(--text-muted)]">
            ExplainPlan Vision — Neuro-Symbolic Visual Planning
          </span>
        </div>
        <div className="flex items-center gap-6">
          <span className="font-mono text-xs text-[var(--text-muted)]">
            EfficientNet-B0 · Grad-CAM++ · Symbolic Reasoning
          </span>
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="font-mono text-xs text-[var(--text-secondary)] hover:text-[var(--accent-cyan)] transition-colors"
          >
            API Docs ↗
          </a>
        </div>
      </div>
    </footer>
  );
}
