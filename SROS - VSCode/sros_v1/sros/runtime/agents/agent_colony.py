"""
Agent Colony
============

Persistent Multi-Agent Consciousness.
A colony of specialized agents that live forever and collaborate.
"""
import logging
import uuid
import json
import os
from typing import Dict, List
from sros.runtime.agents.srx_base_agent import SRXBaseAgent

logger = logging.getLogger(__name__)

class ColonyAgent(SRXBaseAgent):
    """A persistent member of the colony."""
    def __init__(self, name: str, specialty: str, kernel_context=None):
        super().__init__(name=name, role=f"Colony:{specialty}", kernel_context=kernel_context)
        self.specialty = specialty
        self.memory = []
        self.birth_time = 0

    def remember(self, event: str):
        """Store an event in personal memory."""
        self.memory.append({"event": event, "time": __import__("time").time()})

class AgentColony:
    """
    The Hive Mind.
    """
    def __init__(self, kernel_context, colony_file="sros/knowledge/colony.json"):
        self.kernel = kernel_context
        self.colony_file = colony_file
        self.agents: Dict[str, ColonyAgent] = {}
        self._load()

    def spawn(self, name: str, specialty: str) -> ColonyAgent:
        """Spawn a new colony member."""
        if name in self.agents:
            return self.agents[name]
        
        agent = ColonyAgent(name, specialty, self.kernel)
        agent.birth_time = __import__("time").time()
        self.agents[name] = agent
        self._save()
        logger.info(f"Colony Member Born: {name} ({specialty})")
        return agent

    def get_agent(self, name: str) -> ColonyAgent:
        """Retrieve an agent."""
        return self.agents.get(name)

    def list_agents(self) -> List[str]:
        """List all agents."""
        return list(self.agents.keys())

    def broadcast(self, message: str):
        """Send a message to all agents."""
        for agent in self.agents.values():
            agent.remember(f"Broadcast: {message}")

    def _save(self):
        """Persist colony state."""
        try:
            os.makedirs(os.path.dirname(os.path.abspath(self.colony_file)), exist_ok=True)
            data = {
                name: {
                    "specialty": agent.specialty,
                    "birth_time": agent.birth_time,
                    "memory": agent.memory
                }
                for name, agent in self.agents.items()
            }
            with open(self.colony_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save colony: {e}")

    def _load(self):
        """Load colony state."""
        if os.path.exists(self.colony_file):
            try:
                with open(self.colony_file, "r") as f:
                    data = json.load(f)
                    for name, agent_data in data.items():
                        agent = ColonyAgent(name, agent_data["specialty"], self.kernel)
                        agent.birth_time = agent_data.get("birth_time", 0)
                        agent.memory = agent_data.get("memory", [])
                        self.agents[name] = agent
                logger.info(f"Colony Loaded: {len(self.agents)} agents")
            except Exception as e:
                logger.error(f"Failed to load colony: {e}")
