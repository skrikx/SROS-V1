"""
Test Agent Foundry

Verifies that the core SROS agents (Architect, Builder, Tester) can be instantiated
and executed using the new SRXBaseAgent architecture.
"""
import unittest
import sys
import os
from unittest.mock import MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sros.runtime.agents.architect_agent import ArchitectAgent
from sros.runtime.agents.builder_agent import BuilderAgent
from sros.runtime.agents.tester_agent import TesterAgent

class MockKernelContext:
    def __init__(self):
        self.memory = MagicMock()
        self.event_bus = MagicMock()
        self.adapters = MagicMock()

class TestAgentFoundry(unittest.TestCase):
    def setUp(self):
        self.kernel = MockKernelContext()
        
    def test_architect_agent(self):
        print("\n--- Testing Architect Agent ---")
        agent = ArchitectAgent(self.kernel)
        self.assertEqual(agent.name, "SROS Architect")
        self.assertEqual(agent.role, "System Architect")
        
        # Test act (should fail gracefully without adapter)
        response = agent.act("Analyze system latency")
        print(f"Response: {response}")
        self.assertIn("[ERROR]", response)
        
        # Verify event published
        self.kernel.event_bus.publish.assert_called()
        
    def test_builder_agent(self):
        print("\n--- Testing Builder Agent ---")
        agent = BuilderAgent(self.kernel)
        self.assertEqual(agent.name, "SROS Builder")
        
        response = agent.act("Create a new daemon")
        print(f"Response: {response}")
        self.assertIn("[ERROR]", response)
        
    def test_tester_agent(self):
        print("\n--- Testing Tester Agent ---")
        agent = TesterAgent(self.kernel)
        self.assertEqual(agent.name, "SROS Tester")
        
        response = agent.act("Test the new daemon")
        print(f"Response: {response}")
        self.assertIn("[ERROR]", response)

if __name__ == '__main__':
    unittest.main()
