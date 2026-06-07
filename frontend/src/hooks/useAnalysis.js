import { useState, useCallback } from "react";
import { toast } from "react-toastify";
import { runFullAnalysis } from "@/services/analysisService";

const initialState = {
  result: null,
  loading: false,
  error: null,
  progress: 0,
};

export const useAnalysis = () => {
  const [state, setState] = useState(initialState);

  const analyze = useCallback(async (file) => {
    setState({ result: null, loading: true, error: null, progress: 0 });

    try {
      const data = await runFullAnalysis(file, (ev) => {
        if (ev.total) {
          setState((s) => ({
            ...s,
            progress: Math.round((ev.loaded / ev.total) * 100),
          }));
        }
      });

      setState({ result: data, loading: false, error: null, progress: 100 });
      toast.success(`Analysis complete — ${data.prediction.disease}`);
      return data;
    } catch (err) {
      const msg =
        err?.response?.data?.detail || err?.message || "Analysis failed";
      setState({ result: null, loading: false, error: msg, progress: 0 });
      toast.error(msg);
      return null;
    }
  }, []);

  const reset = useCallback(() => {
    setState(initialState);
  }, []);

  return { ...state, analyze, reset };
};
