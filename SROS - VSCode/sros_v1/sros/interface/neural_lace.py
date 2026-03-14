"""
Neural Lace
===========

Real-time Brain Visualization.
Exposes the Associative Memory graph as a live JSON endpoint.
"""
import logging
from fastapi import APIRouter
from typing import Dict, Any
from sros.memory.associative_memory import AssociativeMemory

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/neural-lace", tags=["brain"])

@router.get("/graph")
async def get_brain_graph() -> Dict[str, Any]:
    """
    Return the full memory graph in D3.js-compatible format.
    """
    mem = AssociativeMemory()
    
    # Convert to nodes/links format for D3/Cytoscape
    nodes = []
    for node_id, node_data in mem.nodes.items():
        nodes.append({
            "id": node_id,
            "label": node_data.get("concept", node_id),
            "description": node_data.get("description", ""),
            "tags": node_data.get("tags", []),
            "timestamp": node_data.get("timestamp", 0)
        })
    
    links = []
    for edge in mem.edges:
        links.append({
            "source": edge["source"],
            "target": edge["target"],
            "relation": edge["relation"],
            "timestamp": edge.get("timestamp", 0)
        })
    
    return {
        "nodes": nodes,
        "links": links,
        "meta": {
            "total_nodes": len(nodes),
            "total_links": len(links)
        }
    }

@router.post("/concept")
async def add_concept(concept: str, description: str, tags: list[str] = None):
    """Add a concept to memory."""
    mem = AssociativeMemory()
    mem.add_concept(concept, description, tags or [])
    return {"status": "success", "concept": concept}

@router.post("/link")
async def link_concepts(source: str, target: str, relation: str):
    """Link two concepts."""
    mem = AssociativeMemory()
    mem.link_concepts(source, target, relation)
    return {"status": "success", "link": f"{source} --[{relation}]--> {target}"}
