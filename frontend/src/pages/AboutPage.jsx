import React from "react";
import {
  Brain, Eye, GitBranch, Layers, Clock, Shuffle,
  Users, Network, FlaskConical, Cpu, ExternalLink,
} from "lucide-react";

const stages = [
  { n: "01", icon: Eye,       title: "Vision Classification",     color: "var(--accent-cyan)",   desc: "EfficientNet-B0 classifies the leaf image into one of 15 PlantVillage disease classes. Returns top-3 predictions with calibrated confidence scores, severity estimate, and the healthy/diseased flag." },
  { n: "02", icon: Eye,       title: "Grad-CAM++ Explanation",     color: "var(--accent-green)",  desc: "Gradient-weighted Class Activation Mapping generates a spatial heatmap showing which pixels most strongly activated the winning class. Spatial statistics — infection spread, focus score, activation entropy — are extracted from the heatmap." },
  { n: "03", icon: Brain,     title: "Symbolic Fact Extraction",   color: "var(--accent-violet)", desc: "The vision output and GradCAM statistics are grounded into first-order logic predicates: disease_detected, confidence_level, severity_level, infection_spread, and more. Each fact carries a source tag and confidence value." },
  { n: "04", icon: Network,   title: "Knowledge Graph Inference",  color: "var(--accent-amber)",  desc: "20+ inference rules fire over a disease knowledge graph built on NetworkX. Rules derive urgency score, spread risk, treatment class, isolation requirements, and escalation flags from the symbolic facts." },
  { n: "05", icon: Clock,     title: "Temporal Memory",            color: "var(--accent-cyan)",   desc: "Each analysis is stored in a sliding-window memory buffer. Trend analysis compares the current observation against history to detect severity_trend, urgency_trend, and spread_trend — stable, improving, or worsening." },
  { n: "06", icon: Layers,    title: "Adaptive Plan Generation",   color: "var(--accent-green)",  desc: "Six context mechanisms (disease type, spread pattern, urgency score, seasonal modifiers, severity, temporal trend) jointly adapt a step-numbered treatment plan. Each step carries category and urgency annotations." },
  { n: "07", icon: Shuffle,   title: "Counterfactual Analysis",    color: "var(--accent-violet)", desc: "Four what-if scenarios (early detection, isolated spread, critical severity, healthy baseline) compute alternative plans and their urgency deltas — showing how much the outcome would change under different conditions." },
  { n: "08", icon: GitBranch, title: "Decision Tree Look-ahead",   color: "var(--accent-amber)",  desc: "A probabilistic decision tree is constructed from the plan actions, estimating state transitions and expected urgency at each branch. The tree computes an expected_urgency scalar via leaf-weighted averaging." },
  { n: "09", icon: Users,     title: "Human-Adaptive Explanations",color: "var(--accent-cyan)",  desc: "Three audience-specific natural language explanations are generated: farmer (practical, action-focused), agronomist (technical, treatment-class detail), researcher (full trace including rule firings and confidence propagation)." },
  { n: "10", icon: FlaskConical,title: "Full-Analysis Response",   color: "var(--accent-green)",  desc: "A single JSON object bundles all outputs: prediction, xai, reasoning, plan, counterfactuals, decision_tree, explanations, and trend. One image in — everything out." },
];

const techStack = [
  { name: "EfficientNet-B0", role: "Vision backbone", color: "chip-cyan" },
  { name: "Grad-CAM++",      role: "XAI heatmaps",    color: "chip-green" },
  { name: "NetworkX KG",     role: "Knowledge graph", color: "chip-violet" },
  { name: "FastAPI",         role: "REST backend",    color: "chip-amber" },
  { name: "React 19",        role: "Frontend",        color: "chip-cyan" },
  { name: "Tailwind CSS 4",  role: "Styling",         color: "chip-green" },
  { name: "PlantVillage",    role: "Training dataset",color: "chip-violet" },
  { name: "PyTorch",         role: "ML framework",    color: "chip-amber" },
];

export default function AboutPage() {
  return (
    <div className="max-w-5xl mx-auto px-6 py-12">
      {/* Header */}
      <div className="mb-14 fade-up">
        <p className="section-label mb-2">About</p>
        <h1 className="section-title text-4xl mb-4">ExplainPlan Vision</h1>
        <p
          className="text-base max-w-2xl leading-relaxed"
          style={{ color: "var(--text-secondary)" }}
        >
          An end-to-end neuro-symbolic pipeline that combines deep vision,
          gradient-based explanations, first-order logic reasoning, and
          human-adaptive planning to diagnose and treat plant leaf disease.
        </p>
        <div className="flex gap-3 mt-6">
          <a
            href="https://explain-plan-vision.vercel.app/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-primary"
          >
            <ExternalLink size={13} />
            API Docs
          </a>
          <a
            href="https://explain-plan-vision.vercel.app/redoc"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-outline"
          >
            ReDoc ↗
          </a>
        </div>
      </div>

      {/* Tech stack chips */}
      <div className="mb-14 fade-up-d1">
        <p className="section-label mb-4">Tech Stack</p>
        <div className="flex flex-wrap gap-2">
          {techStack.map((t) => (
            <div key={t.name} className={`chip ${t.color}`}>
              {t.name}
              <span className="opacity-60">· {t.role}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Pipeline stages */}
      <div className="fade-up-d2">
        <p className="section-label mb-6">Pipeline Stages</p>
        <div className="flex flex-col gap-4">
          {stages.map(({ n, icon: Icon, title, color, desc }) => (
            <div
              key={n}
              className="panel p-5 flex gap-5 group hover:border-[var(--border-bright)] transition-all"
            >
              <div className="flex flex-col items-center gap-2 shrink-0">
                <span
                  className="font-mono text-xs"
                  style={{ color: "var(--text-muted)" }}
                >
                  {n}
                </span>
                <div
                  className="w-9 h-9 flex items-center justify-center"
                  style={{
                    background: `${color}18`,
                    border: `1px solid ${color}44`,
                  }}
                >
                  <Icon size={16} style={{ color }} />
                </div>
              </div>
              <div>
                <h3
                  className="font-display font-bold text-base mb-2"
                  style={{
                    color: "var(--text-primary)",
                    fontFamily: "var(--font-display)",
                  }}
                >
                  {title}
                </h3>
                <p
                  className="text-sm leading-relaxed"
                  style={{ color: "var(--text-secondary)" }}
                >
                  {desc}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* API endpoints quick-ref */}
      <div className="mt-14 panel p-6 fade-up-d3">
        <p className="section-label mb-4">API Endpoints</p>
        <div className="flex flex-col gap-2">
          {[
            ["GET", "/api/v1/health", "Server liveness and model status"],
            ["POST", "/api/v1/predict", "Disease classification only"],
            ["POST", "/api/v1/explain", "Grad-CAM++ heatmap only"],
            ["POST", "/api/v1/plan", "Treatment plan only"],
            [
              "POST",
              "/api/v1/full-analysis",
              "Complete 10-stage pipeline (primary)",
            ],
            ["GET", "/api/v1/memory", "Temporal memory state"],
            ["DELETE", "/api/v1/memory", "Clear temporal memory"],
            ["GET", "/api/v1/knowledge-graph", "Knowledge graph metadata"],
          ].map(([method, path, desc]) => (
            <div
              key={path}
              className="flex items-center gap-4 px-3 py-2"
              style={{
                background: "var(--bg-surface)",
                border: "1px solid var(--border-dim)",
              }}
            >
              <span
                className="font-mono text-xs w-14 shrink-0"
                style={{
                  color:
                    method === "GET"
                      ? "var(--accent-green)"
                      : method === "POST"
                        ? "var(--accent-cyan)"
                        : "var(--accent-red)",
                }}
              >
                {method}
              </span>
              <span
                className="font-mono text-xs"
                style={{ color: "var(--text-primary)" }}
              >
                {path}
              </span>
              <span
                className="font-mono text-xs ml-auto hidden md:block"
                style={{ color: "var(--text-muted)" }}
              >
                {desc}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
