
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import uuid
import time

@dataclass(frozen=True)
class EventEnvelope:
    topic: str
    event_type: str
    payload: Dict[str, Any]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)

@dataclass(frozen=True)
class CommandEnvelope:
    target: str
    command: str
    args: Dict[str, Any]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)