import logging
import json
import time
import os
from typing import Dict, Any

logger = logging.getLogger(__name__)

class EvolutionLogger:
    """
    Sovereign Evolution Logger.
    Records all autonomous changes to a persistent JSONL file.
    """
    def __init__(self, log_path: str = "sros/knowledge/evolution_log.jsonl"):
        self.log_path = log_path
        # Ensure dir exists
        os.makedirs(os.path.dirname(os.path.abspath(log_path)), exist_ok=True)

    def log_evolution(self, target: str, plan: str, result: str, success: bool):
        """Log an evolution event."""
        entry = {
            "timestamp": time.time(),
            "target": target,
            "plan": plan,
            "result": result,
            "success": success,
            "agent": "Skrikx Prime"
        }
        
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
            logger.info(f"Evolution logged: {target}")
        except Exception as e:
            logger.error(f"Failed to log evolution: {e}")

    def get_history(self, limit: int = 10):
        """Retrieve recent evolution history."""
        history = []
        if not os.path.exists(self.log_path):
            return history
            
        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                for line in f:
                    history.append(json.loads(line))
        except Exception:
            pass
            
        return history[-limit:]
