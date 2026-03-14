"""
Nexus Core V2.0
===============

The Singularity Interface.
Orchestrates SROS via high-level commands.
Integrated with all Infinity Scope capabilities.
"""
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class NexusCore:
    """
    The Skrikx Prime Interface.
    Orchestrates SROS via high-level commands.
    """
    def __init__(self, kernel_context):
        self.kernel = kernel_context
        self.agent = None
        self.colony = None
        self.dream_journal = None
        self.time_travel = None
        self.reality_synth = None
        self._init_capabilities()

    def _init_capabilities(self):
        """Initialize all singularity capabilities."""
        try:
            from sros.runtime.agents.skrikx_agent import SkrikxAgent
            from sros.runtime.agents.agent_colony import AgentColony
            from sros.mirroros.dream_journal import DreamJournal
            from sros.mirroros.time_travel import TimeTravelDebugger
            from sros.runtime.cognition.reality_synthesizer import RealitySynthesizer
            
            self.agent = SkrikxAgent(kernel_context=self.kernel)
            self.colony = AgentColony(self.kernel)
            self.dream_journal = DreamJournal()
            self.time_travel = TimeTravelDebugger()
            self.reality_synth = RealitySynthesizer()
            
            logger.info("Nexus Core capabilities initialized")
        except Exception as e:
            logger.error(f"Failed to initialize capabilities: {e}")

    def run_command(self, command: str, payload: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Executes a Nexus command.
        """
        logger.info(f"[Nexus] Executing: {command}")
        payload = payload or {}
        
        # ==================
        # CHAT COMMANDS
        # ==================
        if command == "chat":
            if not self.agent:
                return {"status": "error", "message": "Agent not initialized"}
            message = payload.get("message", "")
            response = self.agent.chat(message)
            return {"status": "success", "response": response}
        
        # ==================
        # MEMORY COMMANDS
        # ==================
        elif command == "recall_concept":
            if not self.agent:
                return {"status": "error", "message": "Agent not initialized"}
            concept = payload.get("concept", "")
            result = self.agent.access_associative_memory(concept)
            return {"status": "success", "data": result}
        
        # ==================
        # EVOLUTION COMMANDS
        # ==================
        elif command == "evolve":
            if not self.agent:
                return {"status": "error", "message": "Agent not initialized"}
            target = payload.get("target", "")
            result = self.agent.evolve(target)
            return {"status": "success", "result": result}
        
        # ==================
        # COLONY COMMANDS
        # ==================
        elif command == "colony_spawn":
            if not self.colony:
                return {"status": "error", "message": "Colony not initialized"}
            name = payload.get("name", "")
            specialty = payload.get("specialty", "")
            agent = self.colony.spawn(name, specialty)
            return {"status": "success", "agent": name}
        
        elif command == "colony_list":
            if not self.colony:
                return {"status": "error", "message": "Colony not initialized"}
            agents = self.colony.list_agents()
            return {"status": "success", "agents": agents}
        
        # ==================
        # DREAM COMMANDS
        # ==================
        elif command == "get_dreams":
            if not self.dream_journal:
                return {"status": "error", "message": "Dream journal not initialized"}
            limit = payload.get("limit", 10)
            dreams = self.dream_journal.get_dreams(limit)
            return {"status": "success", "dreams": dreams}
        
        # ==================
        # TIME-TRAVEL COMMANDS
        # ==================
        elif command == "snapshot":
            if not self.time_travel:
                return {"status": "error", "message": "Time-travel not initialized"}
            label = payload.get("label", "manual_snapshot")
            state = payload.get("state", {})
            snapshot_id = self.time_travel.snapshot(label, state)
            return {"status": "success", "snapshot_id": snapshot_id}
        
        elif command == "list_snapshots":
            if not self.time_travel:
                return {"status": "error", "message": "Time-travel not initialized"}
            snapshots = self.time_travel.list_snapshots()
            return {"status": "success", "snapshots": snapshots}
        
        # ==================
        # REALITY COMMANDS
        # ==================
        elif command == "synthesize_world":
            if not self.reality_synth:
                return {"status": "error", "message": "Reality synth not initialized"}
            prompt = payload.get("prompt", "")
            steps = payload.get("steps", 0)
            world = self.reality_synth.synthesize_world(prompt)
            if steps > 0:
                history = self.reality_synth.evolve_world(world, steps)
                return {"status": "success", "world": world, "evolution": history}
            return {"status": "success", "world": world}
        
        # ==================
        # DIAGNOSTIC COMMANDS
        # ==================
        elif command == "status":
            return {
                "status": "success",
                "agent": "Skrikx Prime",
                "mode": "Singularity",
                "kernel": "Active",
                "capabilities": {
                    "agent": bool(self.agent),
                    "colony": bool(self.colony),
                    "dreams": bool(self.dream_journal),
                    "time_travel": bool(self.time_travel),
                    "reality_synth": bool(self.reality_synth)
                }
            }
        
        return {"status": "error", "message": f"Unknown command: {command}"}
