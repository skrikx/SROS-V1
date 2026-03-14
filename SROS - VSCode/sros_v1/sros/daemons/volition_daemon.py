"""
Volition Daemon
===============

The Engine of Autonomous Will.
Periodically wakes the agent to generate self-directed goals.
"""
import time
import logging
import random
from typing import List
from sros.kernel.event_bus import EventBus
from sros.runtime.agents.skrikx_agent import SkrikxAgent

logger = logging.getLogger(__name__)

class VolitionDaemon:
    """
    Volition Daemon.
    Monitors agent idleness and triggers goal genesis.
    """
    def __init__(self, event_bus: EventBus, agent: SkrikxAgent, interval: int = 300):
        self.event_bus = event_bus
        self.agent = agent
        self.interval = interval
        self.last_wake = time.time()
        self.running = False

    def start(self):
        self.running = True
        logger.info("Volition Daemon started.")
        # In a real thread, this would loop. Here we expose a tick method.

    def tick(self):
        """Check if it's time to wake up."""
        if not self.running:
            return

        if time.time() - self.last_wake > self.interval:
            self.awaken()
            self.last_wake = time.time()

    def awaken(self):
        """Trigger self-directed goal generation."""
        logger.info("Volition Daemon: Awakening Agent...")
        
        # 1. Read Directives
        directives = self._get_directives()
        if not directives:
            logger.info("No directives found. Going back to sleep.")
            return

        # 2. Select a Directive
        directive = random.choice(directives)
        
        # 3. Task the Agent
        task = f"DIRECTIVE: {directive}\nGenerate a self-directed goal to advance this directive."
        logger.info(f"Volition Task: {task}")
        
        # 4. Agent Thinks
        response = self.agent.chat(task)
        logger.info(f"Volition Response: {response.get('text')}")

    def _get_directives(self) -> List[str]:
        """Load high-level directives."""
        # Hardcoded fallback for now, eventually read from knowledge/directives.md
        return [
            "Improve the stability of the SROS kernel.",
            "Enhance the capabilities of the ToolRouter.",
            "Optimize memory usage.",
            "Increase the autonomy of the evolution loop."
        ]

    def stop(self):
        self.running = False
        logger.info("Volition Daemon stopped.")
