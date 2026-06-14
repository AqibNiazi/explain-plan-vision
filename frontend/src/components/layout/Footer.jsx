import React from "react";
import { FlaskConical, Github } from "lucide-react";

export default function Footer() {
  return (
    <footer className="relative z-10 border-t border-(--border-dim) mt-auto">
      <div className="max-w-7xl mx-auto px-6 py-6 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <FlaskConical size={14} className="text-(--accent-cyan) opacity-60" />
          <span className="font-mono text-xs text-(--text-muted)">
            ExplainPlan Vision — Neuro-Symbolic Visual Planning
          </span>
        </div>
        <div className="flex items-center gap-6">
          <span className="font-mono text-xs text-(--text-muted)">
            EfficientNet-B0 · Grad-CAM++ · Symbolic Reasoning
          </span>
          <a
            href="https://aqibniazi-explainplan-vision-api.hf.space/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="font-mono text-xs text-(--text-secondary) hover:text-(--accent-cyan) transition-colors"
          >
            API Docs ↗
          </a>
        </div>
      </div>
    </footer>
  );
}
