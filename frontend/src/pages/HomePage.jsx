import React from "react";
import { Link } from "react-router-dom";
import {
  Brain, Eye, GitBranch, BarChart2, Clock, Layers,
  ArrowRight, ChevronRight, Cpu, FlaskConical,
} from "lucide-react";
import { useHealth } from "@/hooks/useHealth";
import { pct } from "@/utils/helpers";

const features = [
  {
    icon: Eye,
    color: "cyan",
    title: "Vision Classification",
    desc: "EfficientNet-B0 trained on PlantVillage — 15 disease classes with confidence scores and top-3 alternatives.",
  },
  {
    icon: Brain,
    color: "green",
    title: "Grad-CAM++ XAI",
    desc: "Spatial heatmaps reveal exactly which leaf regions drove the prediction — trustworthy, interpretable AI.",
  },
  {
    icon: GitBranch,
    color: "violet",
    title: "Symbolic Reasoning",
    desc: "20+ inference rules fire over a disease knowledge graph to derive urgency, spread risk, and treatment class.",
  },
  {
    icon: Layers,
    color: "amber",
    title: "Adaptive Planning",
    desc: "Six context mechanisms dynamically adapt a step-numbered treatment plan to the detected disease state.",
  },
  {
    icon: BarChart2,
    color: "cyan",
    title: "Counterfactual Analysis",
    desc: "Four what-if scenarios show how the plan changes under different conditions — critical for decision confidence.",
  },
  {
    icon: Clock,
    color: "green",
    title: "Temporal Memory",
    desc: "Track disease progression across sessions. Trend analysis flags worsening conditions before they escalate.",
  },
];

const colorMap = {
  cyan:   { border: "rgba(0,229,255,0.25)", glow: "rgba(0,229,255,0.06)", text: "var(--accent-cyan)", icon: "rgba(0,229,255,0.15)" },
  green:  { border: "rgba(0,255,157,0.25)", glow: "rgba(0,255,157,0.06)", text: "var(--accent-green)", icon: "rgba(0,255,157,0.15)" },
  violet: { border: "rgba(124,77,255,0.25)", glow: "rgba(124,77,255,0.06)", text: "var(--accent-violet)", icon: "rgba(124,77,255,0.15)" },
  amber:  { border: "rgba(255,179,0,0.25)", glow: "rgba(255,179,0,0.06)", text: "var(--accent-amber)", icon: "rgba(255,179,0,0.15)" },
};

export default function HomePage() {
  const { health } = useHealth();

  return (
    <div className="max-w-7xl mx-auto px-6 py-20">
      {/* ── Hero ── */}
      <div className="text-center mb-24 fade-up">
        {/* Top chip */}
        <div className="inline-flex items-center gap-2 chip chip-cyan mb-8">
          <Cpu size={11} />
          Neuro-Symbolic Visual Planning Agent
        </div>

        {/* Headline */}
        <h1
          className="text-5xl md:text-7xl font-bold mb-6 leading-tight"
          style={{ fontFamily: "var(--font-display)" }}
        >
          <span className="text-[var(--text-primary)]">Explain</span>
          <span
            className="ml-3"
            style={{
              background: "linear-gradient(135deg, var(--accent-cyan), var(--accent-green))",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            Plant Disease
          </span>
          <br />
          <span className="text-[var(--text-primary)]">with Symbolic AI</span>
        </h1>

        <p
          className="text-lg max-w-2xl mx-auto mb-10"
          style={{ color: "var(--text-secondary)", fontFamily: "var(--font-body)" }}
        >
          Upload a leaf image. Get vision-based classification, Grad-CAM spatial
          explanations, symbolic reasoning traces, adaptive treatment plans, and
          temporal trend analysis — in one pipeline.
        </p>

        {/* CTA buttons */}
        <div className="flex flex-wrap items-center justify-center gap-4">
          <Link to="/analyze" className="btn-primary">
            <FlaskConical size={15} />
            Start Analysis
          </Link>
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-outline"
          >
            API Docs
            <ArrowRight size={14} />
          </a>
        </div>

        {/* Server status strip */}
        {health && (
          <div className="mt-10 inline-flex items-center gap-6 panel px-6 py-3 fade-up-d2">
            <span className="font-mono text-xs text-[var(--text-muted)]">STATUS</span>
            <div className="flex items-center gap-2">
              <div
                className="w-2 h-2 rounded-full"
                style={{
                  background: health.model_loaded ? "var(--accent-green)" : "var(--accent-red)",
                  boxShadow: health.model_loaded ? "0 0 6px var(--accent-green)" : "none",
                  animation: health.model_loaded ? "pulse 2s infinite" : "none",
                }}
              />
              <span className="font-mono text-xs" style={{ color: "var(--text-secondary)" }}>
                {health.model_loaded ? "Model Loaded" : "Model Offline"}
              </span>
            </div>
            <div className="h-divider w-px h-4" style={{ background: "var(--border-base)" }} />
            <span className="font-mono text-xs" style={{ color: "var(--text-secondary)" }}>
              {health.num_classes} Classes · {health.device?.toUpperCase()}
            </span>
            <div className="h-divider w-px h-4" style={{ background: "var(--border-base)" }} />
            <span className="font-mono text-xs" style={{ color: "var(--text-secondary)" }}>
              v{health.version}
            </span>
          </div>
        )}
      </div>

      {/* ── Pipeline steps ── */}
      <div className="mb-24 fade-up-d1">
        <div className="text-center mb-10">
          <p className="section-label mb-2">Analysis Pipeline</p>
          <h2 className="section-title text-3xl">10-Stage Processing</h2>
        </div>
        <div className="flex flex-wrap justify-center gap-0">
          {[
            "Vision", "Grad-CAM++", "Symbolic Facts", "Knowledge Graph",
            "Reasoning", "Temporal Memory", "Adaptive Plan",
            "Counterfactuals", "Decision Tree", "Explanations",
          ].map((step, i) => (
            <React.Fragment key={step}>
              <div
                className="flex flex-col items-center gap-1 px-4 py-3"
                style={{
                  borderTop: "2px solid",
                  borderColor: i % 2 === 0 ? "var(--accent-cyan)" : "var(--border-bright)",
                }}
              >
                <span
                  className="font-mono text-xs"
                  style={{ color: i % 2 === 0 ? "var(--accent-cyan)" : "var(--text-secondary)" }}
                >
                  {String(i + 1).padStart(2, "0")}
                </span>
                <span className="font-mono text-xs text-[var(--text-primary)] whitespace-nowrap">
                  {step}
                </span>
              </div>
              {i < 9 && (
                <div className="flex items-center">
                  <ChevronRight size={14} className="text-[var(--text-muted)]" />
                </div>
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* ── Feature grid ── */}
      <div className="mb-20 fade-up-d2">
        <div className="text-center mb-12">
          <p className="section-label mb-2">Capabilities</p>
          <h2 className="section-title text-3xl">What You Get</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {features.map(({ icon: Icon, color, title, desc }) => {
            const c = colorMap[color];
            return (
              <div
                key={title}
                className="panel p-6 group hover:border-[var(--border-bright)] transition-all duration-300"
                style={{ borderColor: c.border, background: `linear-gradient(135deg, ${c.glow} 0%, var(--bg-panel) 60%)` }}
              >
                <div
                  className="w-10 h-10 flex items-center justify-center mb-4"
                  style={{ background: c.icon, border: `1px solid ${c.border}` }}
                >
                  <Icon size={18} style={{ color: c.text }} />
                </div>
                <h3
                  className="font-display font-700 text-base mb-2"
                  style={{ color: "var(--text-primary)", fontFamily: "var(--font-display)" }}
                >
                  {title}
                </h3>
                <p className="text-sm leading-relaxed" style={{ color: "var(--text-secondary)" }}>
                  {desc}
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* ── CTA bottom ── */}
      <div className="text-center fade-up-d3">
        <div className="panel inline-block px-10 py-10 panel-glow">
          <p className="section-label mb-3">Ready?</p>
          <h3 className="section-title text-2xl mb-4">Upload a Leaf Image</h3>
          <p className="text-sm mb-6" style={{ color: "var(--text-secondary)" }}>
            JPG · PNG · WebP — up to 10 MB
          </p>
          <Link to="/analyze" className="btn-primary">
            <FlaskConical size={15} />
            Open Analyzer
          </Link>
        </div>
      </div>
    </div>
  );
}
