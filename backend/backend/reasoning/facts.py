"""Converts neural outputs into typed symbolic predicates."""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List

import numpy as np
from backend.config import settings


@dataclass
class SymbolicFact:
    predicate  : str
    arguments  : List[str]
    confidence : float
    source     : str
    timestamp  : str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self): return asdict(self)


class SymbolicFactExtractor:

    PATHOGEN_GROUPS = {
        "fungal"   : ["Early blight","Late blight","Leaf Mold","Septoria leaf spot","Target Spot"],
        "bacterial": ["Bacterial spot"],
        "viral"    : ["Tomato YellowLeaf  Curl Virus","Tomato mosaic virus"],
        "pest"     : ["Spider mites Two spotted spider mite"],
        "oomycete" : ["Late blight"],
        "none"     : ["healthy"],
    }
    ENVIRONMENT_MAP = {
        "fungal"   : {"humidity":"high","temperature":"warm", "wetness":"high"},
        "oomycete" : {"humidity":"high","temperature":"cool", "wetness":"high"},
        "bacterial": {"humidity":"high","temperature":"warm", "wetness":"high"},
        "viral"    : {"humidity":"any", "temperature":"any",  "wetness":"low"},
        "pest"     : {"humidity":"low", "temperature":"hot",  "wetness":"low"},
        "none"     : {"humidity":"any", "temperature":"any",  "wetness":"any"},
    }

    def extract(self, prediction: dict, heatmap: np.ndarray) -> List[SymbolicFact]:
        facts = (
            self._vision_facts(prediction)
            + self._spatial_facts(heatmap, prediction["confidence"])
        )
        facts += self._derived_facts(facts, prediction)
        return facts

    def _vision_facts(self, pred: dict) -> List[SymbolicFact]:
        c    = pred["confidence"]
        dt   = pred["disease_type"]
        pt   = self._pathogen_type(dt)
        ru   = pred["top3"][1] if len(pred["top3"]) > 1 else {"disease_class":"none","confidence":0.0}
        return [
            SymbolicFact("disease_is",       [pred["disease"]],          c,              "vision_model"),
            SymbolicFact("disease_type_is",  [dt],                       c,              "vision_model"),
            SymbolicFact("plant_is",         [pred["plant"]],            c,              "vision_model"),
            SymbolicFact("severity_is",      [pred["severity"]],         c,              "vision_model"),
            SymbolicFact("confidence_level", [self._conf_level(c)],      c,              "vision_model"),
            SymbolicFact("pathogen_type_is", [pt],                       c,              "vision_model"),
            SymbolicFact("is_healthy",       [str(pred["is_healthy"])],  c,              "vision_model"),
            SymbolicFact("runner_up_is",     [ru["disease_class"]],      ru["confidence"],"vision_model"),
        ]

    def _spatial_facts(self, heatmap: np.ndarray, conf: float) -> List[SymbolicFact]:
        focus   = float((heatmap >= np.percentile(heatmap, 80)).mean())
        spread  = "localised" if focus < 0.06 else "moderate" if focus < 0.15 else "widespread"
        h       = heatmap.flatten() + 1e-8
        entropy = float(-np.sum((h / h.sum()) * np.log(h / h.sum())))
        return [
            SymbolicFact("infection_spread",   [spread],           conf, "gradcam"),
            SymbolicFact("focus_score",        [f"{focus:.4f}"],   conf, "gradcam"),
            SymbolicFact("activation_entropy", [f"{entropy:.4f}"], conf, "gradcam"),
        ]

    def _derived_facts(self, existing: List[SymbolicFact], pred: dict) -> List[SymbolicFact]:
        fm     = {f.predicate: f.arguments[0] for f in existing}
        pt     = fm.get("pathogen_type_is","unknown")
        sev    = fm.get("severity_is","low")
        spread = fm.get("infection_spread","localised")
        conf   = pred["confidence"]

        treatment_map = {
            "fungal":"fungicide","oomycete":"systemic_fungicide",
            "bacterial":"bactericide","viral":"vector_control",
            "pest":"miticide","none":"monitoring_only",
        }
        derived = [SymbolicFact("treatment_class",
            [treatment_map.get(pt,"expert_consultation")], conf, "derived")]

        crit_diseases  = {"Late blight","Tomato YellowLeaf  Curl Virus"}
        spread_risk    = ("critical" if pred["disease_type"] in crit_diseases else
                          "high"     if spread == "widespread" else "medium")
        derived.append(SymbolicFact("spread_risk", [spread_risk], conf, "derived"))

        urgency_score = (
            conf
            * {"high":3,"medium":2,"low":1}.get(sev,1)
            * {"critical":3,"high":2,"medium":1.5,"low":1,"none":0}.get(spread_risk,1)
        )
        urgency = (
            "immediate" if urgency_score >= 4.5 else
            "high"      if urgency_score >= 3.0 else
            "medium"    if urgency_score >= 1.5 else
            "low"       if not pred["is_healthy"] else "none"
        )
        derived += [
            SymbolicFact("urgency_level", [urgency],               conf, "derived"),
            SymbolicFact("urgency_score", [f"{urgency_score:.4f}"],conf, "derived"),
        ]
        for k, v in self.ENVIRONMENT_MAP.get(pt, {}).items():
            derived.append(SymbolicFact(f"favoured_by_{k}", [v], conf, "derived"))

        needs_iso  = spread_risk == "critical" or (spread == "widespread" and sev == "high")
        needs_chem = pt not in ["none"] and not pred["is_healthy"]
        derived += [
            SymbolicFact("requires_isolation", [str(needs_iso)],  conf, "derived"),
            SymbolicFact("requires_chemical",  [str(needs_chem)], conf, "derived"),
        ]
        return derived

    def _pathogen_type(self, disease_type: str) -> str:
        for pt, diseases in self.PATHOGEN_GROUPS.items():
            if any(d.lower() in disease_type.lower() or disease_type.lower() in d.lower()
                   for d in diseases):
                return pt
        return "unknown"

    @staticmethod
    def _conf_level(c: float) -> str:
        return "very_high" if c >= 0.92 else "high" if c >= 0.80 else "moderate" if c >= 0.60 else "low"
