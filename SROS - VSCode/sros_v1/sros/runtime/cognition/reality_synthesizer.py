"""
Reality Synthesizer
==================

Generate entire simulation environments on demand.
"""
import logging
import json
from typing import Dict, Any, List
from sros.models.model_router import chat

logger = logging.getLogger(__name__)

class RealitySynthesizer:
    """
    The World Builder.
    """
    def synthesize_world(self, prompt: str) -> Dict[str, Any]:
        """
        Generate a complete simulated world.
        """
        system_prompt = """
        You are a Reality Synthesizer.
        Given a world description, generate a complete simulation environment with:
        - Entities (objects, agents, resources)
        - Rules (physics, economics, social)
        - Initial State
        - Victory Conditions
        
        Output as JSON.
        """
        
        full_prompt = f"{system_prompt}\n\nWorld Request: {prompt}"
        response = chat(full_prompt, backend="gemini", temperature=0.8)
        
        try:
            world = json.loads(response.get("text", "{}"))
            logger.info(f"World Synthesized: {prompt[:50]}...")
            return world
        except:
            # Fallback if JSON parsing fails
            return {
                "description": prompt,
                "raw_synthesis": response.get("text", ""),
                "status": "partial"
            }

    def evolve_world(self, world: Dict[str, Any], steps: int = 10) -> List[Dict[str, Any]]:
        """
        Simulate world evolution.
        """
        history = [world]
        current = world
        
        for i in range(steps):
            # Use LLM to predict next state
            prompt = f"Given this world state:\n{json.dumps(current, indent=2)}\n\nPredict the next state after one time step."
            response = chat(prompt, backend="gemini", temperature=0.6)
            
            try:
                next_state = json.loads(response.get("text", "{}"))
                history.append(next_state)
                current = next_state
            except:
                break
                
        return history
