"""
Adapter Daemon

Manages the lifecycle and registry of SROS adapters (Models, Tools, Storage).
Allows hot-swapping of underlying providers without restarting the kernel.
"""
import logging
from typing import Dict, Any, Optional, List
from sros.kernel.event_bus import EventBus
from sros.kernel.channel_types import EventEnvelope, CommandEnvelope

logger = logging.getLogger(__name__)

class AdapterDaemon:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.adapters: Dict[str, Any] = {}
        self.active_models: Dict[str, str] = {} # role -> adapter_id
        
        # Subscribe to adapter commands
        self.event_bus.subscribe("adapter.register", self.handle_register)
        self.event_bus.subscribe("adapter.activate", self.handle_activate)

    def start(self):
        logger.info("Adapter Daemon started")

    def stop(self):
        logger.info("Adapter Daemon stopped")

    def register_adapter(self, adapter_id: str, adapter_instance: Any, metadata: Dict[str, Any] = None):
        """Register a new adapter instance."""
        self.adapters[adapter_id] = {
            "instance": adapter_instance,
            "metadata": metadata or {},
            "status": "registered"
        }
        logger.info(f"Registered adapter: {adapter_id}")
        
        self.event_bus.publish("adapter.registered", {
            "adapter_id": adapter_id,
            "type": metadata.get("type", "unknown")
        })

    def get_adapter(self, adapter_id: str) -> Optional[Any]:
        """Get an adapter instance by ID."""
        entry = self.adapters.get(adapter_id)
        return entry["instance"] if entry else None

    def get_model_for_role(self, role: str) -> Optional[Any]:
        """Get the active model adapter for a specific role (e.g. 'chat', 'embedding')."""
        adapter_id = self.active_models.get(role)
        if not adapter_id:
            # Fallback to default if available
            adapter_id = self.active_models.get("default")
            
        return self.get_adapter(adapter_id)

    def handle_register(self, event: Dict[str, Any]):
        """Handle adapter.register event."""
        payload = event.get("payload", {})
        # In a real implementation, this might load the class dynamically
        logger.info(f"Received register request for {payload.get('adapter_id')}")

    def handle_activate(self, event: Dict[str, Any]):
        """Handle adapter.activate event."""
        payload = event.get("payload", {})
        role = payload.get("role")
        adapter_id = payload.get("adapter_id")
        
        if role and adapter_id and adapter_id in self.adapters:
            self.active_models[role] = adapter_id
            logger.info(f"Activated {adapter_id} for role {role}")
            
            self.event_bus.publish("adapter.activated", {
                "role": role,
                "adapter_id": adapter_id
            })
