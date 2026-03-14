import time
import uuid
import logging
import json
from typing import Callable, Dict, List, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class EventEnvelope:
    id: str
    timestamp: float
    source: str
    topic: str
    payload: Any
    tenant: str = "system"

class EventBus:
    """
    Synchronous in-process event bus.
    """
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}
        self.nexus_bridge = None

    def subscribe(self, topic: str, handler: Callable[[Dict[str, Any]], None]):
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(handler)

    def publish(self, channel: str, event_type: str, payload: Dict[str, Any]):
        """Publish an event to a channel."""
        event = {
            "channel": channel,
            "type": event_type,
            "payload": payload,
            "timestamp": time.time(),
            "id": str(uuid.uuid4())
        }
        
        # 1. Local Subscribers
        if channel in self._subscribers:
            for callback in self._subscribers[channel]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"Error in subscriber for {channel}: {e}")

        # 2. Nexus Stream (Real WebSocket Broadcast)
        self._broadcast_to_nexus(channel, event_type, payload)

    def _broadcast_to_nexus(self, channel: str, event_type: str, payload: Dict[str, Any]):
        """
        Broadcast event to Nexus UI via WebSocket.
        """
        if not self.nexus_bridge:
            try:
                from sros.kernel.nexus_bridge import NexusBridge
                self.nexus_bridge = NexusBridge()
                self.nexus_bridge.start()
            except Exception as e:
                logger.error(f"Failed to initialize Nexus Bridge: {e}")
                self.nexus_bridge = None

        if self.nexus_bridge:
            message = {
                "type": "event",
                "channel": channel,
                "event": event_type,
                "payload": payload,
                "timestamp": time.time()
            }
            self.nexus_bridge.broadcast(message)
