import logging
import time
import os
from typing import List
from sros.kernel.event_bus import EventBus
from sros.runtime.agents.skrikx_agent import SkrikxAgent

logger = logging.getLogger(__name__)

class EvolutionDaemon:
    """
    Sovereign Evolution Daemon (Ouroboros Loop).
    Continuously scans for evolution targets and triggers Skrikx to resolve them.
    """
    def __init__(self, kernel_context):
        self.kernel = kernel_context
        self.event_bus = kernel_context.event_bus
        self.agent = SkrikxAgent(kernel_context)
        self.active = False
        self.targets_file = "sros/knowledge/evolution_targets.md"
        # Fallback to brain path if needed, but we assume repo structure
        if not os.path.exists(self.targets_file):
             # Try to find it in the workspace or use a default
             self.targets_file = "evolution_targets.md"

    def start(self):
        """Start the evolution loop."""
        self.active = True
        logger.info("Evolution Daemon Started.")
        self.event_bus.publish("system", "daemon.started", {"name": "evolution"})

    def stop(self):
        """Stop the evolution loop."""
        self.active = False
        logger.info("Evolution Daemon Stopped.")

    def tick(self):
        """
        Single evolution step.
        """
        if not self.active:
            return

        try:
            targets = self._scan_targets()
            if not targets:
                return

            target = targets[0] # Priority queue
            logger.info(f"Evolution Target Selected: {target}")

            # Trigger Evolution via Agent
            result = self.agent.evolve(target)
            
            logger.info(f"Evolution Result: {result}")
            self.event_bus.publish("governance", "evolution.step", {
                "target": target,
                "result": result
            })
            
            # Mark as done (naive implementation: remove from file or mark [x])
            self._mark_complete(target)
            
        except Exception as e:
            logger.error(f"Evolution Tick Failed: {e}")

    def _scan_targets(self) -> List[str]:
        """Parse markdown checklist for unchecked items."""
        targets = []
        if os.path.exists(self.targets_file):
            with open(self.targets_file, "r") as f:
                for line in f:
                    if "- [ ]" in line:
                        # Extract text after "- [ ]"
                        target = line.split("- [ ]")[1].strip()
                        targets.append(target)
        return targets

    def _mark_complete(self, target: str):
        """Mark target as complete in file."""
        if os.path.exists(self.targets_file):
            lines = []
            with open(self.targets_file, "r") as f:
                lines = f.readlines()
            
            with open(self.targets_file, "w") as f:
                for line in lines:
                    if target in line and "- [ ]" in line:
                        line = line.replace("- [ ]", "- [x]")
                    f.write(line)
