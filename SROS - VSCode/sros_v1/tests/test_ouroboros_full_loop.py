"""
Test Ouroboros Full Loop

Verifies the complete self-evolution cycle with all components wired.
"""
import unittest
import sys
import os
import logging

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sros.evolution.ouroboros import OuroborosLoop
from sros.evolution.types import LoopStage, EvolutionProposal
from sros.evolution.proposer import Proposer
from sros.evolution.simulator import EvolutionSimulator
from sros.evolution.recorder import EvolutionRecorder
from sros.evolution.reviewer import EvolutionReviewer
from sros.kernel.event_bus import EventBus

# Mock Components
class MockObserver:
    def collect(self):
        return {"code_todos": [{"type": "technical_debt", "count": 1, "description": "Fix me", "priority": 5}]}

class MockAnalyzer:
    def analyze(self, observations):
        return observations["code_todos"]

class MockWitness:
    def __init__(self):
        self.traces = []
    def record(self, event_type, payload):
        self.traces.append({"type": event_type, "payload": payload})

class MockKernel:
    def __init__(self):
        self.event_bus = EventBus()
        self.memory = None
        self.witness = MockWitness()

class TestOuroborosLoop(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.INFO)
        self.kernel = MockKernel()
        self.loop = OuroborosLoop(config={"enabled": True, "require_human_approval": False}, kernel_context=self.kernel)
        
        # Inject mocks for stages 1-3 (Observe, Analyze, Propose)
        self.loop.observer = MockObserver()
        self.loop.analyzer = MockAnalyzer()
        self.loop.proposer = Proposer(config={})
        
        # Simulator, Reviewer, Recorder are already wired in __init__ via kernel_context

    def test_full_cycle(self):
        print("\n--- Starting Full Ouroboros Cycle Test ---")
        proposals = self.loop.run_cycle()
        
        self.assertEqual(len(proposals), 1)
        proposal = proposals[0]
        
        print(f"Proposal Generated: {proposal.title}")
        print(f"Final Stage: {proposal.stage}")
        
        # Verify stages
        self.assertEqual(proposal.stage, LoopStage.RECORD)
        self.assertTrue(proposal.approved)
        self.assertIsNotNone(proposal.simulation_results)
        
        # Verify recording
        traces = self.kernel.witness.traces
        self.assertEqual(len(traces), 1)
        self.assertEqual(traces[0]["type"], "evolution.cycle_complete")
        self.assertEqual(traces[0]["payload"]["proposal_id"], proposal.id)
        
        print("✓ Full cycle completed successfully")

if __name__ == '__main__':
    unittest.main()
