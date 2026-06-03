"""Forward-chaining inference engine + knowledge graph traversal."""

from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
from typing import List

from loguru import logger
from backend.config import settings
from backend.reasoning.facts import SymbolicFact
from backend.reasoning.knowledge_graph import DiseaseKnowledgeGraph


@dataclass
class InferenceFact:
    predicate  : str
    arguments  : List[str]
    confidence : float
    rule_fired : str
    support    : List[str]


RULES = [
    ("isolate_critical",
     [("spread_risk","critical"),("is_healthy","False")],
     [("must_isolate",["True"])], 0.95),
    ("isolate_widespread_severe",
     [("infection_spread","widespread"),("severity_is","high"),("is_healthy","False")],
     [("must_isolate",["True"])], 0.90),
    ("systemic_for_oomycete",
     [("pathogen_type_is","oomycete")],
     [("chemical_class",["systemic_fungicide"]),
      ("note",["oomycetes_resist_contact_fungicides"])], 0.95),
    ("contact_fungal_high",
     [("pathogen_type_is","fungal"),("severity_is","high")],
     [("chemical_class",["contact_fungicide"]),("add_preventive_spray",["neighbours"])], 0.90),
    ("contact_fungal_medium",
     [("pathogen_type_is","fungal"),("severity_is","medium")],
     [("chemical_class",["contact_fungicide"])], 0.85),
    ("bactericide",
     [("pathogen_type_is","bacterial")],
     [("chemical_class",["copper_bactericide"]),
      ("note",["bactericides_are_preventive_not_curative"])], 0.90),
    ("vector_control",
     [("pathogen_type_is","viral")],
     [("chemical_class",["insecticide_vector_control"]),
      ("remove_infected_plants",["True"]),
      ("note",["no_chemical_cure_for_viral"])], 0.95),
    ("miticide",
     [("pathogen_type_is","pest")],
     [("chemical_class",["miticide"]),("increase_humidity",["True"])], 0.90),
    ("reduce_humidity_fungal",
     [("pathogen_type_is","fungal"),("favoured_by_humidity","high")],
     [("environmental_action",["reduce_overhead_irrigation"]),
      ("environmental_action",["improve_air_circulation"])], 0.85),
    ("eliminate_wetness_oomycete",
     [("pathogen_type_is","oomycete"),("favoured_by_wetness","high")],
     [("environmental_action",["eliminate_overhead_irrigation"]),
      ("environmental_action",["apply_mulch"])], 0.90),
    ("daily_monitoring",
     [("urgency_level","immediate"),("spread_risk","critical")],
     [("monitoring_frequency",["daily"])], 0.95),
    ("biweekly_monitoring",
     [("urgency_level","high")],
     [("monitoring_frequency",["every_2_days"])], 0.85),
    ("weekly_monitoring",
     [("urgency_level","medium")],
     [("monitoring_frequency",["every_5_days"])], 0.80),
    ("verify_low_confidence",
     [("confidence_level","low")],
     [("add_verification_step",["True"])], 0.90),
    ("verify_critical_moderate",
     [("confidence_level","moderate"),("spread_risk","critical")],
     [("add_verification_step",["True"])], 0.85),
    ("viral_max_alert",
     [("pathogen_type_is","viral"),("spread_risk","critical")],
     [("alert_level",["maximum"]),("report_to_extension",["True"])], 0.95),
    ("preventive_neighbours",
     [("spread_risk","critical"),("infection_spread","widespread")],
     [("preventive_treatment",["neighbouring_plants"])], 0.90),
    ("recovery_fungal",
     [("pathogen_type_is","fungal"),("severity_is","medium")],
     [("recovery_outlook",["good_with_treatment"])], 0.80),
    ("no_recovery_viral",
     [("pathogen_type_is","viral")],
     [("recovery_outlook",["remove_plant"])], 0.95),
    ("healthy_routine",
     [("is_healthy","True")],
     [("action_required",["routine_monitoring_only"]),
      ("monitoring_frequency",["weekly"])], 0.99),
]


class NSReasoningEngine:
    _instance: NSReasoningEngine | None = None

    def __init__(self, kg: DiseaseKnowledgeGraph):
        self.kg    = kg
        self.depth = settings.inference_depth
        logger.info(f"NSReasoningEngine ready | rules={len(RULES)} | depth={self.depth}")

    @classmethod
    def get(cls) -> NSReasoningEngine:
        if cls._instance is None:
            cls._instance = cls(DiseaseKnowledgeGraph.get())
        return cls._instance

    def reason(self, facts: List[SymbolicFact], disease_type: str) -> List[InferenceFact]:
        fm: dict[str, list[str]] = defaultdict(list)
        for f in facts:
            if f.arguments:
                fm[f.predicate].append(f.arguments[0])

        derived: List[InferenceFact] = []
        fired:   set[str]            = set()
        base_conf = facts[0].confidence if facts else 0.8

        for _ in range(self.depth):
            new = []
            for name, preconds, conclusions, cf in RULES:
                if name in fired:
                    continue
                if all(v in fm.get(p, []) for p, v in preconds):
                    support = [f"{p}={v}" for p, v in preconds]
                    for pred, args in conclusions:
                        new.append(InferenceFact(pred, args, round(cf * base_conf, 4), name, support))
                        fm[pred].append(args[0])
                    fired.add(name)
            derived.extend(new)
            if not new:
                break

        # Knowledge graph augmentation
        node = self.kg.node_name(disease_type)
        if node:
            for treat, w in sorted(self.kg.get_treatments(node), key=lambda x: -x[1]):
                derived.append(InferenceFact(
                    "graph_treatment", [treat, f"{w:.2f}"],
                    round(w * base_conf, 4), "kg_traversal", [f"node={node}"]))
            for cf_d in self.kg.get_confusion_pairs(node):
                derived.append(InferenceFact(
                    "confused_with", [cf_d],
                    round(0.7 * base_conf, 4), "kg_confusion", [f"node={node}"]))

        return derived
