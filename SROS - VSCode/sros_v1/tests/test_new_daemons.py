"""
Comprehensive tests for all kernel daemons.
Tests for newly added memory, adapter, and agent_router daemons.
"""
import pytest
import time
import threading
from sros.kernel.event_bus import EventBus
from sros.kernel.daemons.memory_daemon import MemoryDaemon
from sros.kernel.daemons.adapter_daemon import AdapterDaemon
from sros.kernel.daemons.agent_router_daemon import AgentRouterDaemon
from sros.memory.memory_router import MemoryRouter


class TestMemoryDaemon:
    """Test memory daemon functionality."""
    
    @pytest.fixture
    def event_bus(self):
        return EventBus()
    
    @pytest.fixture
    def memory_router(self):
        return MemoryRouter()
    
    @pytest.fixture
    def memory_daemon(self, event_bus, memory_router):
        daemon = MemoryDaemon(event_bus, memory_router=memory_router, check_interval=0.5)
        yield daemon
        if daemon.running:
            daemon.stop()
    
    def test_memory_daemon_init(self, memory_daemon):
        """Test memory daemon initialization."""
        assert not memory_daemon.running
        assert memory_daemon.migrations_count == 0
        assert memory_daemon.cleanup_runs == 0
    
    def test_memory_daemon_start_stop(self, memory_daemon, event_bus):
        """Test memory daemon start and stop."""
        memory_daemon.start()
        assert memory_daemon.running
        
        # Let it run briefly
        time.sleep(0.2)
        
        memory_daemon.stop()
        assert not memory_daemon.running
    
    def test_memory_daemon_runs_cleanup(self, memory_daemon, event_bus):
        """Test that memory daemon performs cleanup."""
        memory_daemon.start()
        time.sleep(1.0)  # Let daemon run for one cycle
        memory_daemon.stop()
        
        assert memory_daemon.cleanup_runs > 0
    
    def test_memory_daemon_get_status(self, memory_daemon):
        """Test getting memory daemon status."""
        memory_daemon.start()
        time.sleep(0.3)
        
        status = memory_daemon.get_status()
        assert status["running"] == True
        assert "cleanup_runs" in status
        assert "migrations_count" in status
        
        memory_daemon.stop()
    
    def test_memory_daemon_double_start(self, memory_daemon):
        """Test that double-start doesn't error."""
        memory_daemon.start()
        memory_daemon.start()  # Should log warning but not error
        
        assert memory_daemon.running
        memory_daemon.stop()


class TestAdapterDaemon:
    """Test adapter daemon functionality."""
    
    @pytest.fixture
    def event_bus(self):
        return EventBus()
    
    @pytest.fixture
    def adapter_daemon(self, event_bus):
        daemon = AdapterDaemon(event_bus, check_interval=0.5)
        yield daemon
        if daemon.running:
            daemon.stop()
    
    def test_adapter_daemon_init(self, adapter_daemon):
        """Test adapter daemon initialization."""
        assert not adapter_daemon.running
        assert len(adapter_daemon.adapter_health) == 0
    
    def test_adapter_daemon_register(self, adapter_daemon):
        """Test registering adapters."""
        adapter_daemon.register_adapter("gemini", "model", {"api_key": "test"})
        adapter_daemon.register_adapter("openai", "model", {"api_key": "test"})
        
        assert len(adapter_daemon.adapter_health) == 2
        assert "gemini" in adapter_daemon.adapter_health
        assert "openai" in adapter_daemon.adapter_health
    
    def test_adapter_daemon_unregister(self, adapter_daemon):
        """Test unregistering adapters."""
        adapter_daemon.register_adapter("test", "model", {})
        assert len(adapter_daemon.adapter_health) == 1
        
        adapter_daemon.unregister_adapter("test")
        assert len(adapter_daemon.adapter_health) == 0
    
    def test_adapter_daemon_start_stop(self, adapter_daemon, event_bus):
        """Test adapter daemon start and stop."""
        adapter_daemon.register_adapter("test", "model", {})
        
        adapter_daemon.start()
        assert adapter_daemon.running
        time.sleep(0.3)
        
        adapter_daemon.stop()
        assert not adapter_daemon.running
    
    def test_adapter_daemon_health_check(self, adapter_daemon):
        """Test health check runs."""
        adapter_daemon.register_adapter("test", "model", {})
        adapter_daemon.start()
        time.sleep(0.7)  # Let it run through one check cycle
        
        status = adapter_daemon.get_adapter_status("test")
        assert status is not None
        assert "health" in status
        assert "error_count" in status
        
        adapter_daemon.stop()
    
    def test_adapter_daemon_get_status(self, adapter_daemon):
        """Test getting daemon status."""
        adapter_daemon.register_adapter("test1", "model", {})
        adapter_daemon.register_adapter("test2", "model", {})
        
        adapter_daemon.start()
        time.sleep(0.3)
        
        status = adapter_daemon.get_status()
        assert status["running"] == True
        assert status["adapters_total"] == 2
        
        adapter_daemon.stop()
    
    def test_adapter_daemon_get_all_status(self, adapter_daemon):
        """Test getting status of all adapters."""
        adapter_daemon.register_adapter("adapter1", "model", {})
        adapter_daemon.register_adapter("adapter2", "tool", {})
        
        statuses = adapter_daemon.get_all_adapters_status()
        assert len(statuses) == 2
        assert any(s["adapter_name"] == "adapter1" for s in statuses)
        assert any(s["adapter_name"] == "adapter2" for s in statuses)


class TestAgentRouterDaemon:
    """Test agent router daemon functionality."""
    
    @pytest.fixture
    def event_bus(self):
        return EventBus()
    
    @pytest.fixture
    def agent_router(self, event_bus):
        daemon = AgentRouterDaemon(event_bus, check_interval=0.5)
        yield daemon
        if daemon.running:
            daemon.stop()
    
    def test_agent_router_init(self, agent_router):
        """Test agent router initialization."""
        assert not agent_router.running
        assert len(agent_router.agents) == 0
    
    def test_agent_router_register(self, agent_router):
        """Test registering agents."""
        agent_router.register_agent("tester", "test_agent", ["test_generation"])
        agent_router.register_agent("architect", "design_agent", ["design"])
        
        assert len(agent_router.agents) == 2
        assert "tester" in agent_router.agents
        assert "architect" in agent_router.agents
    
    def test_agent_router_register_capabilities(self, agent_router):
        """Test agent capabilities storage."""
        agent_router.register_agent("agent1", "type1", ["cap1", "cap2"])
        
        assert agent_router.agent_capabilities["agent1"] == ["cap1", "cap2"]
    
    def test_agent_router_unregister(self, agent_router):
        """Test unregistering agents."""
        agent_router.register_agent("test", "type", [])
        assert len(agent_router.agents) == 1
        
        agent_router.unregister_agent("test")
        assert len(agent_router.agents) == 0
    
    def test_agent_router_route_to_specific_agent(self, agent_router):
        """Test routing message to specific agent."""
        agent_router.register_agent("target", "type", [])
        
        message = {"content": "test", "priority": 1}
        result = agent_router.route_message(message, agent_id="target")
        
        assert result == True
        assert agent_router.routed_messages == 1
        assert len(agent_router.agent_queue["target"]) == 1
    
    def test_agent_router_route_by_capability(self, agent_router):
        """Test routing message by required capability."""
        agent_router.register_agent("agent1", "type", ["analysis"])
        agent_router.register_agent("agent2", "type", ["synthesis"])
        
        message = {"content": "analyze", "data": [1, 2, 3]}
        result = agent_router.route_message(message, capability_required="analysis")
        
        assert result == True
        assert len(agent_router.agent_queue["agent1"]) == 1
        assert len(agent_router.agent_queue["agent2"]) == 0
    
    def test_agent_router_load_balancing(self, agent_router):
        """Test load balancing across agents with same capability."""
        agent_router.register_agent("agent1", "type", ["process"])
        agent_router.register_agent("agent2", "type", ["process"])
        
        # Add message to agent1
        agent_router.agent_queue["agent1"].append({"msg": "1"})
        
        # Route new message should go to agent2 (fewer pending)
        result = agent_router.route_message({"content": "test"}, capability_required="process")
        
        assert result == True
        assert len(agent_router.agent_queue["agent1"]) == 1
        assert len(agent_router.agent_queue["agent2"]) == 1
    
    def test_agent_router_route_not_found(self, agent_router):
        """Test routing to nonexistent agent fails."""
        result = agent_router.route_message({"content": "test"}, agent_id="nonexistent")
        
        assert result == False
        assert agent_router.failed_routes == 1
    
    def test_agent_router_route_no_capability(self, agent_router):
        """Test routing with missing capability fails."""
        agent_router.register_agent("agent1", "type", ["other"])
        
        result = agent_router.route_message({"content": "test"}, capability_required="missing")
        
        assert result == False
        assert agent_router.failed_routes == 1
    
    def test_agent_router_get_pending_messages(self, agent_router):
        """Test retrieving pending messages."""
        agent_router.register_agent("agent1", "type", [])
        
        msg1 = {"id": 1}
        msg2 = {"id": 2}
        agent_router.agent_queue["agent1"].append(msg1)
        agent_router.agent_queue["agent1"].append(msg2)
        
        messages = agent_router.get_pending_messages("agent1")
        
        assert len(messages) == 2
        assert messages[0]["id"] == 1
        assert messages[1]["id"] == 2
        # Queue should be cleared after retrieval
        assert len(agent_router.agent_queue["agent1"]) == 0
    
    def test_agent_router_get_agent_status(self, agent_router):
        """Test getting agent status."""
        agent_router.register_agent("test", "type", ["cap1", "cap2"])
        agent_router.route_message({"content": "test"}, agent_id="test")
        
        status = agent_router.get_agent_status("test")
        
        assert status is not None
        assert status["agent_id"] == "test"
        assert status["message_count"] == 1
        assert "pending_messages" in status
    
    def test_agent_router_start_stop(self, agent_router, event_bus):
        """Test agent router start and stop."""
        agent_router.register_agent("test", "type", [])
        
        agent_router.start()
        assert agent_router.running
        time.sleep(0.3)
        
        agent_router.stop()
        assert not agent_router.running
    
    def test_agent_router_get_status(self, agent_router):
        """Test getting router status."""
        agent_router.register_agent("agent1", "type", [])
        agent_router.register_agent("agent2", "type", [])
        agent_router.route_message({"content": "test"}, agent_id="agent1")
        
        status = agent_router.get_status()
        
        assert status["running"] == False
        assert status["agents_registered"] == 2
        assert status["routed_messages"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
