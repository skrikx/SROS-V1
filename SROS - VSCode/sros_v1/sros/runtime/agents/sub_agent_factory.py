"""
Sub-Agent Factory
=================

Spawns lightweight sub-agents for parallel task execution.
Enables unbounded recursion and swarm intelligence.
"""
import logging
import uuid
from typing import Dict, Any
from sros.runtime.agents.srx_base_agent import SRXBaseAgent
from sros.models.model_router import chat

logger = logging.getLogger(__name__)

class SubAgent(SRXBaseAgent):
    """Lightweight sub-agent."""
    def __init__(self, name: str, role: str, parent_id: str, kernel_context=None):
        super().__init__(name=name, role=role, kernel_context=kernel_context)
        self.parent_id = parent_id

    def run_task(self, task: str) -> str:
        """Execute a single task."""
        prompt = f"""
        You are a Sub-Agent spawned by {self.parent_id}.
        Role: {self.role}
        Task: {task}
        
        Execute the task and return the result.
        """
        response = chat(prompt, backend="gemini", temperature=0.5)
        return response.get("text", "Task failed.")

class SubAgentFactory:
    """
    Factory for spawning sub-agents.
    """
    def __init__(self, kernel_context):
        self.kernel_context = kernel_context
        self.active_agents: Dict[str, SubAgent] = {}

    def spawn_agent(self, role: str, task: str) -> str:
        """
        Spawn a new sub-agent to handle a task.
        """
        agent_id = f"sub_agent_{uuid.uuid4().hex[:8]}"
        agent = SubAgent(name=agent_id, role=role, parent_id="SkrikxPrime", kernel_context=self.kernel_context)
        self.active_agents[agent_id] = agent
        
        logger.info(f"Spawned Sub-Agent {agent_id} for role: {role}")
        
        # Execute task immediately (synchronous for now)
        result = agent.run_task(task)
        
        # Cleanup
        del self.active_agents[agent_id]
        
        return f"Sub-Agent {agent_id} Result: {result}"
