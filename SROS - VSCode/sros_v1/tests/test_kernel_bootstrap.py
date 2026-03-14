"""
Test Kernel Bootstrap

Verifies that the SROS Kernel boots correctly with all components initialized.
"""
import unittest
import sys
import os
import shutil
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sros.kernel.kernel_bootstrap import boot, KernelContext

class TestKernelBootstrap(unittest.TestCase):
    def test_kernel_boot(self):
        print("\n--- Testing Kernel Boot ---")
        
        # Boot kernel
        kernel = boot(config_path="test_config.yml")
        
        # Verify Context
        self.assertIsInstance(kernel, KernelContext)
        self.assertIsNotNone(kernel.event_bus)
        self.assertIsNotNone(kernel.memory)
        self.assertIsNotNone(kernel.registry)
        self.assertIsNotNone(kernel.witness)
        
        # Verify Memory Layers
        print("Verifying Memory Layers...")
        self.assertIsNotNone(kernel.memory.short_term)
        self.assertIsNotNone(kernel.memory.long_term)
        self.assertIsNotNone(kernel.memory.codex)
        self.assertIsNotNone(kernel.memory.vector_store)
        
        # Verify Daemons
        print("Verifying Daemons...")
        daemons = kernel.registry.daemons
        self.assertIn("heartbeat", daemons)
        self.assertIn("scheduler", daemons)
        self.assertIn("health", daemons)
        self.assertIn("memory", daemons)
        self.assertIn("adapter", daemons)
        self.assertIn("agent_router", daemons)
        
        # Verify Daemons Running
        running = kernel.registry.running
        self.assertTrue(running.get("heartbeat"))
        self.assertTrue(running.get("adapter"))
        
        # Stop Daemons
        kernel.registry.stop_all()

if __name__ == '__main__':
    unittest.main()
