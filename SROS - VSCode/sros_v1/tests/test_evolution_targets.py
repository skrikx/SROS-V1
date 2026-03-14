"""
Test Evolution Targets

Verifies that the newly created modules can be imported and instantiated.
"""
import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sros.kernel.channel_types import Event, Command
from sros.kernel.daemons.heartbeat_daemon import HeartbeatDaemon
from sros.kernel.daemons.adapter_daemon import AdapterDaemon
from sros.runtime.tool_router import ToolRouter
from sros.runtime.agents.srx_memory_curator_agent import SRXMemoryCuratorAgent
from sros.runtime.agents.srx_simulation_agent import SRXSimulationAgent
from sros.governance.kpi_tracker import KPITracker
from sros.mirroros.replay_engine import ReplayEngine
from sros.kernel.event_bus import EventBus

class TestEvolutionTargets(unittest.TestCase):
    def setUp(self):
        self.event_bus = EventBus()

    def test_channel_types(self):
        event = Event(source="test", topic="test.topic", payload={})
        self.assertEqual(event.type.value, "event")
        print("✓ Channel Types verified")

    def test_heartbeat_daemon(self):
        daemon = HeartbeatDaemon(self.event_bus)
        status = daemon.get_status()
        self.assertEqual(status["status"], "stopped")
        print("✓ Heartbeat Daemon verified")

    def test_adapter_daemon(self):
        daemon = AdapterDaemon(self.event_bus)
        self.assertIsNotNone(daemon.adapters)
        print("✓ Adapter Daemon verified")

    def test_tool_router(self):
        router = ToolRouter(self.event_bus)
        self.assertIsNotNone(router.tools)
        print("✓ Tool Router verified")

    def test_agents(self):
        # Mock Kernel Context
        class MockKernel:
            def __init__(self, bus):
                self.event_bus = bus
                self.memory = None
        
        kernel = MockKernel(self.event_bus)
        
        curator = SRXMemoryCuratorAgent(kernel)
        self.assertEqual(curator.role, "Memory Curator")
        
        sim_agent = SRXSimulationAgent(kernel)
        self.assertEqual(sim_agent.role, "Simulation Driver")
        print("✓ Runtime Agents verified")

    def test_governance_mirror(self):
        tracker = KPITracker()
        tracker.record("test_metric", 1.0)
        metrics = tracker.get_metrics("test_metric")
        self.assertEqual(metrics["count"], 1)
        
        engine = ReplayEngine()
        self.assertIsNone(engine.active_replay)
        print("✓ Governance & MirrorOS verified")

if __name__ == '__main__':
    unittest.main()
