"""
Agent Router Daemon

Manages agent discovery, routing, and dynamic dispatcher.
Coordinates agent execution and message passing.
"""
import time
import threading
import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentRouterDaemon:
    """
    Agent Router Daemon - Manage agent discovery and routing.
    
    Features:
    - Agent registration and discovery
    - Dynamic agent routing based on capability
    - Message queue and dispatching
    - Load balancing across agent instances
    - Event bus integration for inter-agent communication
    """
    
    def __init__(self, event_bus, check_interval: float = 5.0):
        """
        Initialize agent router daemon.
        
        Args:
            event_bus: Event bus for publishing events
            check_interval: How often to check agent health (seconds)
        """
        self.event_bus = event_bus
        self.check_interval = check_interval
        self.running = False
        self._thread = None
        self._lock = threading.RLock()
        
        # Agent registry
        self.agents: Dict[str, Dict[str, Any]] = {}  # agent_id -> agent_info
        self.agent_capabilities: Dict[str, List[str]] = {}  # agent_id -> capabilities
        self.agent_queue: Dict[str, List[Dict[str, Any]]] = {}  # agent_id -> message_queue
        
        # Statistics
        self.routed_messages = 0
        self.failed_routes = 0
        self.last_check = None
    
    def start(self):
        """Start agent router daemon."""
        if self.running:
            logger.warning("Agent router daemon already running")
            return
        
        self.running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        
        logger.info("Agent router daemon started")
        self.event_bus.publish("agent_router", "agent_router.started", {
            "timestamp": datetime.now().isoformat()
        })
    
    def stop(self):
        """Stop agent router daemon."""
        self.running = False
        if self._thread:
            self._thread.join(timeout=5)
        
        logger.info("Agent router daemon stopped")
        self.event_bus.publish("agent_router", "agent_router.stopped", {
            "timestamp": datetime.now().isoformat()
        })
    
    def register_agent(self, agent_id: str, agent_type: str, capabilities: List[str]):
        """
        Register an agent for routing.
        
        Args:
            agent_id: Unique agent identifier
            agent_type: Type of agent (tester, architect, builder, etc.)
            capabilities: List of agent capabilities
        """
        with self._lock:
            self.agents[agent_id] = {
                "agent_type": agent_type,
                "registered_at": datetime.now(),
                "last_activity": datetime.now(),
                "message_count": 0
            }
            self.agent_capabilities[agent_id] = capabilities
            self.agent_queue[agent_id] = []
            
            logger.info(f"Registered agent: {agent_id} ({agent_type}) with capabilities: {capabilities}")
            self.event_bus.publish("agent_router", "agent.registered", {
                "agent_id": agent_id,
                "agent_type": agent_type,
                "capabilities": capabilities,
                "timestamp": datetime.now().isoformat()
            })
    
    def unregister_agent(self, agent_id: str):
        """Unregister an agent."""
        with self._lock:
            if agent_id in self.agents:
                del self.agents[agent_id]
            if agent_id in self.agent_capabilities:
                del self.agent_capabilities[agent_id]
            if agent_id in self.agent_queue:
                del self.agent_queue[agent_id]
            
            logger.info(f"Unregistered agent: {agent_id}")
            self.event_bus.publish("agent_router", "agent.unregistered", {
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat()
            })
    
    def route_message(
        self,
        message: Dict[str, Any],
        capability_required: Optional[str] = None,
        agent_id: Optional[str] = None
    ) -> bool:
        """
        Route a message to appropriate agent(s).
        
        Args:
            message: Message to route
            capability_required: Required capability (if any)
            agent_id: Specific agent ID (optional)
        
        Returns:
            True if routed successfully
        """
        with self._lock:
            if agent_id:
                # Route to specific agent
                if agent_id not in self.agents:
                    self.failed_routes += 1
                    logger.warning(f"Agent {agent_id} not found for routing")
                    return False
                
                self.agent_queue[agent_id].append(message)
                self.agents[agent_id]["message_count"] += 1
                self.agents[agent_id]["last_activity"] = datetime.now()
                self.routed_messages += 1
                
                return True
            
            elif capability_required:
                # Route to agent with required capability
                matching_agents = [
                    aid for aid, caps in self.agent_capabilities.items()
                    if capability_required in caps
                ]
                
                if not matching_agents:
                    self.failed_routes += 1
                    logger.warning(f"No agent with capability {capability_required}")
                    return False
                
                # Load balance: send to agent with fewest pending messages
                target_agent = min(
                    matching_agents,
                    key=lambda aid: len(self.agent_queue[aid])
                )
                
                self.agent_queue[target_agent].append(message)
                self.agents[target_agent]["message_count"] += 1
                self.agents[target_agent]["last_activity"] = datetime.now()
                self.routed_messages += 1
                
                logger.debug(f"Routed message to {target_agent} ({capability_required})")
                return True
            
            else:
                self.failed_routes += 1
                logger.warning("Route message missing agent_id and capability_required")
                return False
    
    def get_pending_messages(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get pending messages for an agent."""
        with self._lock:
            if agent_id not in self.agent_queue:
                return []
            
            messages = self.agent_queue[agent_id]
            self.agent_queue[agent_id] = []  # Clear after retrieval
            
            return messages
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get status of specific agent."""
        with self._lock:
            if agent_id not in self.agents:
                return None
            
            agent_info = self.agents[agent_id]
            return {
                "agent_id": agent_id,
                "agent_type": agent_info["agent_type"],
                "capabilities": self.agent_capabilities.get(agent_id, []),
                "message_count": agent_info["message_count"],
                "pending_messages": len(self.agent_queue.get(agent_id, [])),
                "last_activity": agent_info["last_activity"].isoformat()
            }
    
    def get_all_agents_status(self) -> List[Dict[str, Any]]:
        """Get status of all registered agents."""
        with self._lock:
            return [
                {
                    "agent_id": agent_id,
                    "agent_type": self.agents[agent_id]["agent_type"],
                    "capabilities": self.agent_capabilities.get(agent_id, []),
                    "message_count": self.agents[agent_id]["message_count"],
                    "pending_messages": len(self.agent_queue.get(agent_id, [])),
                    "last_activity": self.agents[agent_id]["last_activity"].isoformat()
                }
                for agent_id in self.agents.keys()
            ]
    
    def _run(self):
        """Main daemon loop."""
        logger.info(f"Agent router daemon loop started (check_interval={self.check_interval}s)")
        
        while self.running:
            try:
                self._monitor_agents()
                self.last_check = datetime.now()
            except Exception as e:
                logger.error(f"Error in agent router daemon: {e}")
                self.event_bus.publish("agent_router", "agent_router.error", {
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
            
            # Sleep but check running status frequently
            for _ in range(int(self.check_interval * 10)):
                if not self.running:
                    break
                time.sleep(0.1)
    
    def _monitor_agents(self):
        """Monitor active agents for timeout/inactivity."""
        with self._lock:
            now = datetime.now()
            inactive_timeout = 300  # 5 minutes
            
            for agent_id, agent_info in list(self.agents.items()):
                time_since_activity = (now - agent_info["last_activity"]).total_seconds()
                
                if time_since_activity > inactive_timeout:
                    logger.warning(f"Agent {agent_id} inactive for {time_since_activity}s")
                    self.event_bus.publish("agent_router", "agent.inactive", {
                        "agent_id": agent_id,
                        "inactive_seconds": int(time_since_activity),
                        "timestamp": now.isoformat()
                    })
    
    def get_status(self) -> Dict[str, Any]:
        """Get daemon status."""
        with self._lock:
            return {
                "running": self.running,
                "agents_registered": len(self.agents),
                "routed_messages": self.routed_messages,
                "failed_routes": self.failed_routes,
                "pending_messages_total": sum(
                    len(q) for q in self.agent_queue.values()
                ),
                "last_check": self.last_check.isoformat() if self.last_check else None,
                "check_interval": self.check_interval
            }
