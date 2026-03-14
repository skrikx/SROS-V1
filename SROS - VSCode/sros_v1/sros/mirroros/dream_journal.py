"""
Dream Journal
=============

Persistent log of all self-generated evolution targets.
"""
import json
import os
import time
import logging

logger = logging.getLogger(__name__)

class DreamJournal:
    """
    Records the dreams of the Ouroboros.
    """
    def __init__(self, journal_path="sros/knowledge/dream_log.jsonl"):
        self.journal_path = journal_path

    def record_dream(self, dream: str, source="ouroboros"):
        """Record a dream."""
        entry = {
            "dream": dream,
            "source": source,
            "timestamp": time.time(),
            "executed": False
        }
        
        try:
            os.makedirs(os.path.dirname(os.path.abspath(self.journal_path)), exist_ok=True)
            with open(self.journal_path, "a") as f:
                f.write(json.dumps(entry) + "\n")
            logger.info(f"Dream Recorded: {dream[:50]}...")
        except Exception as e:
            logger.error(f"Failed to record dream: {e}")

    def get_dreams(self, limit=10) -> list:
        """Retrieve recent dreams."""
        dreams = []
        if os.path.exists(self.journal_path):
            try:
                with open(self.journal_path, "r") as f:
                    for line in f:
                        dreams.append(json.loads(line))
                # Return most recent
                return dreams[-limit:]
            except Exception as e:
                logger.error(f"Failed to read dreams: {e}")
        return dreams
