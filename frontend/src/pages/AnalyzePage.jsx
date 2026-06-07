import React, { useState } from "react";
import {
  FlaskConical, Loader2, RotateCcw, Clock, Zap,
} from "lucide-react";
import ImageUploader from "@/components/ui/ImageUploader.jsx";
import PredictionCard from "@/components/analysis/PredictionCard.jsx";
import XAICard from "@/components/analysis/XAICard.jsx";
import ReasoningCard from "@/components/analysis/ReasoningCard.jsx";
import PlanCard from "@/components/analysis/PlanCard.jsx";
import CounterfactualsCard from "@/components/analysis/CounterfactualsCard.jsx";
import ExplanationsCard from "@/components/analysis/ExplanationsCard.jsx";
import TrendCard from "@/components/analysis/TrendCard.jsx";
import { useAnalysis } from "@/hooks/useAnalysis.js";
import { b64src } from "@/utils/helpers.js";

export default function AnalyzePage() {
  const [file, setFile] = useState(null);
  const { result, loading, error, progress, analyze, reset } = useAnalysis();

  const handleAnalyze = async () => {
    if (!file) return;
    await analyze(file);
  };

  const handleReset = () => {
    setFile(null);
    reset();
  };

  return (
    <div className="max-w-7xl mx-auto px-6 py-12">
      {/* Page header */}
      <div className="mb-10 fade-up">
        <p className="section-label mb-2">Analysis</p>
        <h1 className="section-title text-4xl mb-3">Plant Disease Analyzer</h1>
        <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
          Upload a leaf image to run the full 10-stage neuro-symbolic pipeline.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* ── Left column: upload + controls ── */}
        <div className="lg:col-span-1 flex flex-col gap-4 fade-up-d1">
          {/* Upload panel */}
          <div className="panel p-4">
            <p className="section-label mb-3">Input Image</p>
            <ImageUploader onFile={setFile} disabled={loading} />

            {/* Progress */}
            {loading && (
              <div className="mt-4">
                <div className="flex justify-between mb-1">
                  <span className="font-mono text-xs" style={{ color: "var(--text-muted)" }}>
                    Uploading…
                  </span>
                  <span className="font-mono text-xs" style={{ color: "var(--accent-cyan)" }}>
                    {progress}%
                  </span>
                </div>
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: `${progress}%` }} />
                </div>
              </div>
            )}

            {/* Buttons */}
            <div className="flex gap-3 mt-4">
              <button
                onClick={handleAnalyze}
                disabled={!file || loading}
                className="btn-primary flex-1 justify-center disabled:opacity-40 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <Loader2 size={15} className="animate-spin" />
                ) : (
                  <Zap size={15} />
                )}
                {loading ? "Analyzing…" : "Analyze"}
              </button>
              {(result || error) && (
                <button onClick={handleReset} className="btn-outline px-3">
                  <RotateCcw size={14} />
                </button>
              )}
            </div>
          </div>

          {/* Processing info */}
          {result && (
            <div className="panel p-4 fade-up">
              <p className="section-label mb-3">Run Info</p>
              <div className="flex flex-col gap-2">
                <div className="flex justify-between">
                  <span className="font-mono text-xs" style={{ color: "var(--text-muted)" }}>Request ID</span>
                  <span className="font-mono text-xs" style={{ color: "var(--text-secondary)" }}>
                    {result.request_id?.slice(0, 16)}…
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="font-mono text-xs" style={{ color: "var(--text-muted)" }}>Processing</span>
                  <span className="font-mono text-xs" style={{ color: "var(--accent-cyan)" }}>
                    {result.processing_time_ms?.toFixed(0)} ms
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="font-mono text-xs" style={{ color: "var(--text-muted)" }}>Expected Urgency</span>
                  <span className="font-mono text-xs" style={{ color: "var(--accent-amber)" }}>
                    {result.expected_urgency?.toFixed(3)}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Error */}
          {error && (
            <div
              className="panel p-4 fade-up font-mono text-xs"
              style={{ borderColor: "rgba(255,64,96,0.4)", color: "var(--accent-red)" }}
            >
              ⚠ {error}
            </div>
          )}

          {/* Loading status */}
          {loading && (
            <div className="panel p-4 fade-up">
              <p className="section-label mb-3">Pipeline Progress</p>
              {[
                "Vision Classification",
                "Grad-CAM++ Heatmap",
                "Symbolic Fact Extraction",
                "Knowledge Graph Inference",
                "Temporal Memory Update",
                "Adaptive Plan Generation",
                "Counterfactual Analysis",
                "Decision Tree Construction",
                "Human-Adaptive Explanations",
              ].map((stage, i) => (
                <div key={stage} className="flex items-center gap-2 py-1.5">
                  <div
                    className="w-1.5 h-1.5 rounded-full"
                    style={{
                      background: "var(--accent-cyan)",
                      boxShadow: "0 0 4px var(--accent-cyan)",
                      animation: `pulse ${1 + i * 0.15}s ease-in-out infinite`,
                    }}
                  />
                  <span className="font-mono text-xs" style={{ color: "var(--text-secondary)" }}>
                    {stage}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* ── Right columns: results ── */}
        <div className="lg:col-span-2">
          {!result && !loading && (
            <div
              className="panel flex flex-col items-center justify-center py-24 text-center"
              style={{ minHeight: 400 }}
            >
              <FlaskConical size={40} style={{ color: "var(--border-bright)", marginBottom: 16 }} />
              <p className="font-display font-bold text-xl mb-2" style={{ fontFamily: "var(--font-display)", color: "var(--text-secondary)" }}>
                Awaiting Leaf Image
              </p>
              <p className="font-mono text-xs" style={{ color: "var(--text-muted)" }}>
                Upload an image and click Analyze to begin
              </p>
            </div>
          )}

          {result && (
            <div className="flex flex-col gap-5 fade-up">
              {/* Row 1: Prediction + XAI */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                <PredictionCard prediction={result.prediction} />
                <XAICard
                  xai={result.xai}
                  imageSrc={b64src(result.prediction?.image_b64)}
                />
              </div>

              {/* Row 2: Reasoning + Plan */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                <ReasoningCard reasoning={result.reasoning} />
                <PlanCard plan={result.plan} />
              </div>

              {/* Row 3: Explanations */}
              <ExplanationsCard explanations={result.explanations} />

              {/* Row 4: Counterfactuals + Trend */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                <CounterfactualsCard counterfactuals={result.counterfactuals} />
                <TrendCard trend={result.trend} />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
