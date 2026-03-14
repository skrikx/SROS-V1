"""
System Prompt Evolver
=====================

Meta-Learning Module.
Analyzes agent performance and evolves the system prompt.
"""
import logging
from typing import List, Dict, Any
from sros.models.model_router import chat
from sros.runtime.agents.skrikx_agent import SkrikxAgent

logger = logging.getLogger(__name__)

class SystemPromptEvolver:
    """
    Evolves the system prompt based on interaction history.
    """
    def __init__(self, agent: SkrikxAgent):
        self.agent = agent

    def evolve_prompt(self, history: List[Dict[str, Any]]) -> str:
        """
        Analyze history and propose prompt updates.
        """
        logger.info("Analyzing history for prompt evolution...")
        
        # 1. Extract recent interactions
        interactions = "\n".join([f"{h.get('role')}: {h.get('content')}" for h in history[-20:]])
        
        # 2. Meta-Prompt
        meta_prompt = f"""
        You are an AGI Architect optimizing an agent's system prompt.
        
        Current System Prompt:
        {self.agent.system_prompt[:1000]}... (truncated)
        
        Recent Interactions:
        {interactions}
        
        Task:
        Analyze the interactions. Identify weaknesses, confusion, or inefficiencies.
        Propose specific edits to the system prompt to improve performance.
        
        Output format:
        <analysis>...</analysis>
        <proposal>...</proposal>
        """
        
        # 3. Call Model
        response = chat(meta_prompt, backend="openai", temperature=0.7)
        proposal = response.get("text", "No proposal generated.")
        
        logger.info(f"Evolution Proposal: {proposal[:100]}...")
        return proposal

    def apply_update(self, new_prompt_segment: str):
        """
        Apply the update (Placeholder).
        In a real system, this would use edit_file to patch skrikx_prime.xml.
        """
        # Safety: Don't auto-apply without review yet.
        logger.info(f"Proposed Update: {new_prompt_segment}")
        # self.agent.chat(f"TOOL: edit_file ...") 
