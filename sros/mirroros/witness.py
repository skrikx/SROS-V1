import time
import uuid
from typing import Any, Dict, Optional

from .trace_store import TraceStore

class Witness:
    """
    Observes the system and records traces.
    """
    def __init__(self, trace_store):
        self.trace_store = trace_store

    def record(
        self,
        event_type: str,
        payload: Dict[str, Any],
        *,
        source: str = "runtime",
        topic: str = "workflow",
        run_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ):
        """
        Record an event to the trace store.
        """
        envelope_payload = payload or {}
        resolved_run_id = run_id or envelope_payload.get("run_id")
        trace = {
            "event_id": str(uuid.uuid4()),
            "timestamp": time.time(),
            "event_type": event_type,
            "source": source,
            "topic": topic,
            "run_id": resolved_run_id,
            "correlation_id": correlation_id,
            "payload": envelope_payload,
        }
        self.trace_store.append(trace)
        
    def log_event(self, envelope):
        """
        Convert envelope to dict and log.
        """
        trace = {
            "event_id": envelope.id,
            "timestamp": envelope.timestamp,
            "event_type": envelope.topic,
            "source": envelope.source,
            "topic": envelope.topic,
            "run_id": getattr(envelope, "run_id", None),
            "correlation_id": getattr(envelope, "correlation_id", None),
            "payload": envelope.payload
        }
        self.trace_store.append(trace)
