import { useState, useEffect } from "react";
import { fetchHealth } from "@/services/analysisService";

export const useHealth = () => {
  const [health, setHealth] = useState(null);
  const [checking, setChecking] = useState(true);

  const check = async () => {
    try {
      const data = await fetchHealth();
      setHealth(data);
    } catch {
      setHealth({ status: "offline", model_loaded: false });
    } finally {
      setChecking(false);
    }
  };

  useEffect(() => {
    check();
    const interval = setInterval(check, 30000);
    return () => clearInterval(interval);
  }, []);

  return { health, checking, refetch: check };
};
