"""Typed directed knowledge graph: disease–pathogen–treatment–environment."""

from __future__ import annotations
from typing import List, Tuple

import networkx as nx
from loguru import logger


class DiseaseKnowledgeGraph:
    _instance: DiseaseKnowledgeGraph | None = None

    def __init__(self):
        self.G = nx.DiGraph()
        self._build()
        logger.info(f"KnowledgeGraph ready | nodes={self.G.number_of_nodes()} | edges={self.G.number_of_edges()}")

    @classmethod
    def get(cls) -> DiseaseKnowledgeGraph:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _build(self):
        G = self.G
        nodes = {
            # Diseases
            "Early_blight"         :{"type":"disease","pathogen_type":"fungal",  "spread":"medium"},
            "Late_blight"          :{"type":"disease","pathogen_type":"oomycete","spread":"critical"},
            "Bacterial_spot"       :{"type":"disease","pathogen_type":"bacterial","spread":"high"},
            "Septoria_leaf_spot"   :{"type":"disease","pathogen_type":"fungal",  "spread":"medium"},
            "Leaf_Mold"            :{"type":"disease","pathogen_type":"fungal",  "spread":"medium"},
            "Target_Spot"          :{"type":"disease","pathogen_type":"fungal",  "spread":"medium"},
            "Spider_mites"         :{"type":"disease","pathogen_type":"pest",    "spread":"high"},
            "YellowLeaf_Curl_Virus":{"type":"disease","pathogen_type":"viral",   "spread":"critical"},
            "Mosaic_Virus"         :{"type":"disease","pathogen_type":"viral",   "spread":"high"},
            "Healthy"              :{"type":"disease","pathogen_type":"none",    "spread":"none"},
            # Pathogens
            "Alternaria_solani"    :{"type":"pathogen"},
            "Phytophthora_infestans":{"type":"pathogen"},
            "Xanthomonas_spp"      :{"type":"pathogen"},
            "Septoria_lycopersici" :{"type":"pathogen"},
            "Passalora_fulva"      :{"type":"pathogen"},
            "TYLCV"                :{"type":"pathogen"},
            "ToMV"                 :{"type":"pathogen"},
            # Treatments
            "Copper_fungicide"     :{"type":"treatment","mode":"contact"},
            "Metalaxyl"            :{"type":"treatment","mode":"systemic"},
            "Mancozeb"             :{"type":"treatment","mode":"contact"},
            "Copper_bactericide"   :{"type":"treatment","mode":"contact"},
            "Imidacloprid"         :{"type":"treatment","mode":"systemic"},
            "Abamectin"            :{"type":"treatment","mode":"contact"},
            "Physical_removal"     :{"type":"treatment","mode":"physical"},
            "Isolation"            :{"type":"treatment","mode":"physical"},
            "Monitoring"           :{"type":"treatment","mode":"observational"},
            # Environments
            "High_humidity"        :{"type":"environment"},
            "Cool_temperature"     :{"type":"environment"},
            "Leaf_wetness"         :{"type":"environment"},
            "Low_humidity"         :{"type":"environment"},
            "Whitefly_vector"      :{"type":"environment"},
        }
        for n, a in nodes.items():
            G.add_node(n, **a)

        for s, d, r, w in [
            ("Early_blight","Alternaria_solani","caused_by",1.0),
            ("Late_blight","Phytophthora_infestans","caused_by",1.0),
            ("Bacterial_spot","Xanthomonas_spp","caused_by",1.0),
            ("Septoria_leaf_spot","Septoria_lycopersici","caused_by",1.0),
            ("YellowLeaf_Curl_Virus","TYLCV","caused_by",1.0),
            ("Mosaic_Virus","ToMV","caused_by",1.0),
            ("Early_blight","Copper_fungicide","treated_by",0.90),
            ("Early_blight","Physical_removal","treated_by",0.80),
            ("Late_blight","Metalaxyl","treated_by",0.95),
            ("Late_blight","Mancozeb","treated_by",0.90),
            ("Late_blight","Isolation","treated_by",0.95),
            ("Late_blight","Physical_removal","treated_by",0.85),
            ("Bacterial_spot","Copper_bactericide","treated_by",0.90),
            ("Bacterial_spot","Physical_removal","treated_by",0.80),
            ("Septoria_leaf_spot","Mancozeb","treated_by",0.85),
            ("Leaf_Mold","Copper_fungicide","treated_by",0.85),
            ("Spider_mites","Abamectin","treated_by",0.90),
            ("YellowLeaf_Curl_Virus","Imidacloprid","treated_by",0.85),
            ("YellowLeaf_Curl_Virus","Physical_removal","treated_by",0.80),
            ("Mosaic_Virus","Physical_removal","treated_by",0.80),
            ("Healthy","Monitoring","treated_by",1.00),
            ("Late_blight","High_humidity","favoured_by",0.8),
            ("Late_blight","Cool_temperature","favoured_by",0.8),
            ("Late_blight","Leaf_wetness","favoured_by",0.8),
            ("Early_blight","High_humidity","favoured_by",0.8),
            ("Bacterial_spot","High_humidity","favoured_by",0.8),
            ("Spider_mites","Low_humidity","favoured_by",0.8),
            ("YellowLeaf_Curl_Virus","Whitefly_vector","favoured_by",0.8),
            ("Late_blight","Early_blight","confused_with",0.6),
            ("Early_blight","Late_blight","confused_with",0.6),
            ("YellowLeaf_Curl_Virus","Mosaic_Virus","confused_with",0.6),
            ("Mosaic_Virus","YellowLeaf_Curl_Virus","confused_with",0.6),
        ]:
            G.add_edge(s, d, relation=r, weight=w)

    def get_treatments(self, node: str) -> List[Tuple[str, float]]:
        return [(n, self.G[node][n]["weight"]) for n in self.G.successors(node)
                if self.G[node][n].get("relation") == "treated_by"]

    def get_confusion_pairs(self, node: str) -> List[str]:
        return [n for n in self.G.successors(node)
                if self.G[node][n].get("relation") == "confused_with"]

    def shortest_path(self, source: str, target: str):
        try:
            path  = nx.shortest_path(self.G, source, target)
            edges = [(path[i], path[i+1], self.G[path[i]][path[i+1]].get("relation","?"))
                     for i in range(len(path)-1)]
            return path, edges
        except nx.NetworkXNoPath:
            return [], []

    def node_name(self, disease_type: str) -> str | None:
        mapping = {
            "Late blight":"Late_blight","Early blight":"Early_blight",
            "Bacterial spot":"Bacterial_spot","Septoria leaf spot":"Septoria_leaf_spot",
            "Leaf Mold":"Leaf_Mold","Target Spot":"Target_Spot",
            "Spider mites Two spotted spider mite":"Spider_mites",
            "Tomato YellowLeaf  Curl Virus":"YellowLeaf_Curl_Virus",
            "Tomato mosaic virus":"Mosaic_Virus","healthy":"Healthy",
        }
        for k, v in mapping.items():
            if k.lower() in disease_type.lower() or disease_type.lower() in k.lower():
                return v
        return None
