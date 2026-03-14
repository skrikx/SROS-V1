"""
Test Evolution API Endpoint Logic

Simulates the logic inside the /api/evolution/cycle endpoint to debug potential crashes.
"""
import unittest
import sys
import os
import logging

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestEvolutionEndpoint(unittest.TestCase):
    def test_trigger_evolution_cycle(self):
        print("\n--- Testing Evolution Endpoint Logic ---")
        try:
            from sros.evolution.ouroboros import OuroborosLoop
            
            print("Initializing OuroborosLoop...")
            # Initialize loop (mimicking routes.py)
            loop = OuroborosLoop(config={"enabled": True})
            
            print("Running cycle...")
            # Run cycle
            proposals = loop.run_cycle()
            
            print(f"Cycle complete. Proposals: {len(proposals)}")
            
            response = {
                "status": "success",
                "message": "Evolution cycle initiated",
                "proposals_count": len(proposals),
                "proposals": [p.title for p in proposals]
            }
            print(f"Response: {response}")
            self.assertEqual(response["status"], "success")
            
        except Exception as e:
            print(f"FAILED with error: {e}")
            import traceback
            traceback.print_exc()
            self.fail(f"Endpoint logic failed: {e}")

if __name__ == '__main__':
    unittest.main()
