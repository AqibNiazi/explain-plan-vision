import React, { useEffect, useState } from "react";
import { Clock, Trash2, RefreshCw, Database } from "lucide-react";
import { fetchMemory, clearMemory } from "@/services/analysisService.js";
import { toast } from "react-toastify";
import { trendIcon, urgencyChip } from "@/utils/helpers.js";

export default function MemoryPage() {
  const [memory, setMemory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [clearing, setClearing] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const data = await fetchMemory();
      setMemory(data);
    } catch (e) {
      toast.error("Failed to load memory");
    } finally {
      setLoading(false);
    }
  };

  const handleClear = async () => {
    if (!confirm("Clear all temporal memory? This cannot be undone.")) return;
    setClearing(true);
    try {
      await clearMemory();
      toast.success("Memory cleared");
      await load();
    } catch {
      toast.error("Failed to clear memory");
    } finally {
      setClearing(false);
    }
  };

  useEffect(() => { load(); }, []);

  return (
    <div className="max-w-5xl mx-auto px-6 py-12">
      {/* Header */}
      <div className="flex items-start justify-between mb-10 fade-up">
        <div>
          <p className="section-label mb-2">Memory</p>
          <h1 className="section-title text-4xl mb-3">Temporal Memory</h1>
          <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
            Track disease progression across analysis sessions.
          </p>
        </div>
        <div className="flex gap-3 mt-2">
          <button onClick={load} disabled={loading} className="btn-outline">
            <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
            Refresh
          </button>
          <button onClick={handleClear} disabled={clearing || loading} className="btn-outline" style={{ color: "var(--accent-red)", borderColor: "var(--accent-red)" }}>
            <Trash2 size={14} />
            Clear
          </button>
        </div>
      </div>

      {loading && (
        <div className="panel flex items-center justify-center py-20">
          <RefreshCw size={24} className="animate-spin" style={{ color: "var(--accent-cyan)" }} />
        </div>
      )}

      {!loading && memory && (
        <div className="flex flex-col gap-6 fade-up">
          {/* Stats row */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: "Observations", value: memory.n_observations, color: "var(--accent-cyan)" },
              { label: "Capacity", value: memory.capacity, color: "var(--text-secondary)" },
              { label: "Disease Stable", value: memory.trend.disease_stable ? "Yes" : "No", color: memory.trend.disease_stable ? "var(--accent-green)" : "var(--accent-red)" },
              { label: "Latest Severity", value: memory.trend.latest_severity, color: "var(--accent-amber)" },
            ].map(({ label, value, color }) => (
              <div key={label} className="panel p-4 text-center">
                <p className="font-mono text-xs mb-2" style={{ color: "var(--text-muted)" }}>{label}</p>
                <p className="font-mono text-lg font-bold" style={{ color }}>{value}</p>
              </div>
            ))}
          </div>

          {/* Trend panel */}
          <div className="panel p-6">
            <p className="section-label mb-4">Trend Analysis</p>
            {memory.trend.summary && (
              <div
                className="px-3 py-2 mb-4 font-mono text-xs"
                style={{ background: "var(--bg-surface)", borderLeft: "2px solid var(--accent-green)", color: "var(--text-secondary)" }}
              >
                {memory.trend.summary}
              </div>
            )}
            <div className="grid grid-cols-3 gap-4">
              {[
                ["Severity", memory.trend.severity_trend],
                ["Urgency",  memory.trend.urgency_trend],
                ["Spread",   memory.trend.spread_trend],
              ].map(([label, val]) => (
                <div key={label} className="p-3 text-center" style={{ background: "var(--bg-surface)", border: "1px solid var(--border-dim)" }}>
                  <p className="font-mono text-xs mb-1" style={{ color: "var(--text-muted)" }}>{label}</p>
                  <p className="font-mono text-sm capitalize" style={{
                    color: val === "improving" ? "var(--accent-green)" : val === "worsening" ? "var(--accent-red)" : "var(--text-secondary)"
                  }}>
                    {trendIcon(val)} {val}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Monitoring recommendation */}
          {memory.monitoring_recommendation && (
            <div
              className="panel p-5 flex items-start gap-3"
              style={{ borderColor: "rgba(0,229,255,0.3)" }}
            >
              <Clock size={16} style={{ color: "var(--accent-cyan)", marginTop: 2 }} />
              <div>
                <p className="font-mono text-xs uppercase tracking-widest mb-1" style={{ color: "var(--accent-cyan)" }}>
                  Monitoring Recommendation
                </p>
                <p className="text-sm" style={{ color: "var(--text-primary)" }}>
                  {memory.monitoring_recommendation}
                </p>
              </div>
            </div>
          )}

          {/* Entries table */}
          {memory.entries?.length > 0 && (
            <div className="panel p-6">
              <p className="section-label mb-4">Observation History ({memory.entries.length})</p>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr style={{ borderBottom: "1px solid var(--border-base)" }}>
                      {["#", "Disease", "Severity", "Urgency", "Timestamp"].map((h) => (
                        <th key={h} className="text-left pb-2 font-mono text-xs" style={{ color: "var(--text-muted)" }}>
                          {h}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {memory.entries.map((e, i) => (
                      <tr key={i} style={{ borderBottom: "1px solid var(--border-dim)" }}>
                        <td className="py-2 font-mono text-xs" style={{ color: "var(--text-muted)" }}>{i + 1}</td>
                        <td className="py-2 font-mono text-xs" style={{ color: "var(--text-primary)" }}>{e.disease || "—"}</td>
                        <td className="py-2"><span className={`chip ${e.severity === "high" ? "chip-red" : e.severity === "medium" ? "chip-amber" : "chip-green"}`}>{e.severity || "—"}</span></td>
                        <td className="py-2"><span className={`chip ${urgencyChip(e.urgency_level)}`}>{e.urgency_level || "—"}</span></td>
                        <td className="py-2 font-mono text-xs" style={{ color: "var(--text-muted)" }}>
                          {e.timestamp ? new Date(e.timestamp * 1000).toLocaleString() : "—"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {memory.n_observations === 0 && (
            <div className="panel flex flex-col items-center justify-center py-16 text-center">
              <Database size={32} style={{ color: "var(--border-bright)", marginBottom: 12 }} />
              <p className="font-mono text-sm" style={{ color: "var(--text-secondary)" }}>No observations yet</p>
              <p className="font-mono text-xs mt-1" style={{ color: "var(--text-muted)" }}>
                Run an analysis to populate temporal memory
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
