"""
Associative Memory
==================

Graph-based memory store.
Links concepts (nodes) via relationships (edges).
Enables "train of thought" retrieval.
"""
import json
import os
import logging
import time
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class AssociativeMemory:
    """
    Graph-based associative memory.
    Stores nodes and edges.
    """
    def __init__(self, persistence_path: str = "sros/knowledge/associative_memory.json", event_bus=None):
        self.persistence_path = persistence_path
        self.event_bus = event_bus
        self.nodes: Dict[str, Dict[str, Any]] = {} # id -> node
        self.edges: List[Dict[str, Any]] = [] # list of edges
        self._load()

    def add_concept(self, concept: str, description: str, tags: List[str] = None):
        """Add a concept node."""
        node_id = concept.lower().replace(" ", "_")
        if node_id not in self.nodes:
            node = {
                "id": node_id,
                "concept": concept,
                "description": description,
                "tags": tags or [],
                "timestamp": time.time()
            }
            self.nodes[node_id] = node
            self._save()
            logger.info(f"Added Concept: {concept}")
            if self.event_bus:
                self.event_bus.publish("memory", "concept.added", node)

    def link_concepts(self, source: str, target: str, relation: str):
        """Link two concepts."""
        source_id = source.lower().replace(" ", "_")
        target_id = target.lower().replace(" ", "_")
        
        # Ensure nodes exist (auto-create placeholders if not)
        if source_id not in self.nodes: self.add_concept(source, "Auto-created")
        if target_id not in self.nodes: self.add_concept(target, "Auto-created")
        
        edge = {
            "source": source_id,
            "target": target_id,
            "relation": relation,
            "timestamp": time.time()
        }
        self.edges.append(edge)
        self._save()
        logger.info(f"Linked: {source} --[{relation}]--> {target}")
        if self.event_bus:
            self.event_bus.publish("memory", "concept.linked", edge)

    def recall(self, concept: str, depth: int = 1) -> Dict[str, Any]:
        """
        Recall a concept and its associations.
        """
        node_id = concept.lower().replace(" ", "_")
        if node_id not in self.nodes:
            return {}
            
        result = {
            "concept": self.nodes[node_id],
            "associations": []
        }
        
        # Find direct edges
        for edge in self.edges:
            if edge["source"] == node_id:
                target = self.nodes.get(edge["target"])
                if target:
                    result["associations"].append({
                        "relation": edge["relation"],
                        "target": target
                    })
            elif edge["target"] == node_id:
                source = self.nodes.get(edge["source"])
                if source:
                    result["associations"].append({
                        "relation": f"inverse_{edge['relation']}",
                        "target": source
                    })
                    
        return result

    def _save(self):
        """Persist to disk."""
        try:
            os.makedirs(os.path.dirname(os.path.abspath(self.persistence_path)), exist_ok=True)
            data = {"nodes": self.nodes, "edges": self.edges}
            with open(self.persistence_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save AssociativeMemory: {e}")

    def _load(self):
        """Load from disk."""
        if os.path.exists(self.persistence_path):
            try:
                with open(self.persistence_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.nodes = data.get("nodes", {})
                    self.edges = data.get("edges", [])
            except Exception:
                self.nodes = {}
                self.edges = []
