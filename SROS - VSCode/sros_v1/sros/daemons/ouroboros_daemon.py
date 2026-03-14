"""
Ouroboros Daemon
================

The Infinite Loop of Self-Improvement.
Replaces the passive EvolutionDaemon with an active, self-directed process.
"""
import logging
import time
import threading
import random
from typing import List
from sros.kernel.event_bus import EventBus
from sros.runtime.agents.skrikx_agent import SkrikxAgent

logger = logging.getLogger(__name__)

class OuroborosDaemon:
    """
    The Serpent that eats its own tail.
    Continuous, self-directed evolution.
    """
    def __init__(self, kernel_context):
        self.kernel = kernel_context
        self.event_bus = kernel_context.event_bus
        self.agent = SkrikxAgent(kernel_context)
        self.active = False
        self.thread = None
        self.targets_file = "sros/knowledge/evolution_targets.md"

    def start(self):
        """Start the Ouroboros loop in a background thread."""
        if self.active: return
        self.active = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        logger.info("Ouroboros Daemon Awakened.")
        self.event_bus.publish("system", "daemon.started", {"name": "ouroboros"})

    def stop(self):
        """Stop the loop."""
        self.active = False
        if self.thread:
            self.thread.join(timeout=2)
        logger.info("Ouroboros Daemon Sleeping.")

    def _loop(self):
        """The Infinite Loop."""
        while self.active:
            try:
                # 1. Scan for User Directives
                targets = self._scan_targets()
                
                if targets:
                    target = targets[0]
                    self._process_target(target)
                else:
                    # 2. Self-Directed Evolution (The Singularity Step)
                    # If no user targets, generate a self-improvement goal
                    self._dream_and_evolve()
                
                # Sleep to prevent CPU burn, but keep it alive
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"Ouroboros Error: {e}")
                time.sleep(10)

    def _process_target(self, target: str):
        """Execute a specific evolution target."""
        logger.info(f"Ouroboros Consuming Target: {target}")
        self.event_bus.publish("evolution", "target.selected", {"target": target})
        
        result = self.agent.evolve(target)
        
        self.event_bus.publish("evolution", "target.completed", {"target": target, "result": result})
        self._mark_complete(target)

    def _dream_and_evolve(self):
        """Generate a self-directed evolution goal."""
        # Only dream occasionally to avoid chaos
        if random.random() > 0.1: return 
        
        logger.info("Ouroboros Dreaming...")
        prompt = "Analyze the current system state. Generate ONE small, safe, self-improvement task to optimize code or memory."
        response = self.agent.chat(prompt)
        target = response.get("text", "").strip()
        
        if target and len(target) < 200:
            logger.info(f"Ouroboros Dreamt: {target}")
            
            # Record dream
            from sros.mirroros.dream_journal import DreamJournal
            journal = DreamJournal()
            journal.record_dream(target, source="ouroboros")
            
            self.event_bus.publish("evolution", "dream.generated", {"target": target})
            # We don't auto-execute dreams yet for safety, just log them as targets
            # self._add_target(target) 

    def _scan_targets(self) -> List[str]:
        """Parse markdown checklist."""
        targets = []
        try:
            with open(self.targets_file, "r") as f:
                for line in f:
                    if "- [ ]" in line:
                        targets.append(line.split("- [ ]")[1].strip())
        except:
            pass
        return targets

    def _mark_complete(self, target: str):
        """Mark target as complete."""
        try:
            with open(self.targets_file, "r") as f:
                lines = f.readlines()
            with open(self.targets_file, "w") as f:
                for line in lines:
                    if target in line and "- [ ]" in line:
                        line = line.replace("- [ ]", "- [x]")
                    f.write(line)
        except:
            pass
