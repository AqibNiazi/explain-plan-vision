"""
Rolling temporal memory — stores past observations and computes trend signals
used by the planning engine to escalate or de-escalate treatment urgency.
"""

from __future__ import annotations
from collections import deque
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List

from loguru import logger
from backend.config import settings


@dataclass
class MemoryEntry:
    timestamp        : str
    image_path       : str
    disease_type     : str
    confidence       : float
    severity         : str
    urgency_level    : str
    urgency_score    : float
    infection_spread : str
    is_healthy       : bool
    key_inferences   : List[str]

    def to_dict(self): return asdict(self)


class TemporalMemory:
    """Singleton rolling memory. Persists for the lifetime of the server process."""

    _instance: TemporalMemory | None = None

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.entries  = deque(maxlen=capacity)
        logger.info(f"TemporalMemory ready | capacity={capacity}")

    @classmethod
    def get(cls) -> TemporalMemory:
        if cls._instance is None:
            cls._instance = cls(settings.memory_capacity)
        return cls._instance

    def add(self, entry: MemoryEntry):
        self.entries.append(entry)

    def __len__(self):
        return len(self.entries)

    def get_trend(self) -> dict:
        if len(self.entries) < 2:
            return {
                "severity_trend"  : "insufficient_data",
                "urgency_trend"   : "insufficient_data",
                "spread_trend"    : "insufficient_data",
                "disease_stable"  : True,
                "n_observations"  : len(self.entries),
                "latest_urgency"  : self.entries[-1].urgency_level if self.entries else "unknown",
                "latest_severity" : self.entries[-1].severity      if self.entries else "unknown",
                "summary"         : "Insufficient observation history for trend analysis.",
            }

        entries    = list(self.entries)
        sev_map    = {"high": 3, "medium": 2, "low": 1}
        sev_scores = [sev_map.get(e.severity, 1) for e in entries]
        sev_delta  = sev_scores[-1] - sev_scores[0]
        sev_trend  = "increasing" if sev_delta > 0 else "decreasing" if sev_delta < 0 else "stable"

        urg_scores = [e.urgency_score for e in entries]
        urg_delta  = urg_scores[-1] - urg_scores[0]
        urg_trend  = "increasing" if urg_delta > 0.5 else "decreasing" if urg_delta < -0.5 else "stable"

        spread_map  = {"localised": 1, "moderate": 2, "widespread": 3}
        sp_scores   = [spread_map.get(e.infection_spread, 2) for e in entries]
        sp_delta    = sp_scores[-1] - sp_scores[0]
        sp_trend    = "spreading" if sp_delta > 0 else "contained" if sp_delta < 0 else "stable"

        disease_stable = len(set(e.disease_type for e in entries[-3:])) == 1

        if all(e.is_healthy for e in entries[-3:]):
            summary = f"Plant healthy for {min(3, len(entries))} consecutive observations."
        else:
            summary = (
                f"Severity is {sev_trend}, spread is {sp_trend}. "
                f"Urgency {'escalating' if urg_trend == 'increasing' else 'reducing' if urg_trend == 'decreasing' else 'stable'}. "
                f"Disease {'consistent' if disease_stable else 'varying'} across recent observations."
            )

        return {
            "severity_trend"  : sev_trend,
            "urgency_trend"   : urg_trend,
            "spread_trend"    : sp_trend,
            "disease_stable"  : disease_stable,
            "n_observations"  : len(entries),
            "latest_urgency"  : entries[-1].urgency_level,
            "latest_severity" : entries[-1].severity,
            "summary"         : summary,
        }

    def recommend_monitoring(self) -> str:
        t = self.get_trend()
        if t["severity_trend"] == "increasing" or t["spread_trend"] == "spreading":
            return "Every 24 hours — situation is deteriorating."
        if t["severity_trend"] == "decreasing" and t["spread_trend"] == "contained":
            return "Every 5 days — treatment appears to be working."
        return "Every 2-3 days — standard for this risk level."

    def clear(self):
        self.entries.clear()
        logger.info("TemporalMemory cleared")

    def to_list(self) -> list:
        return [e.to_dict() for e in self.entries]
