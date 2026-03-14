"""
Test Knowledge API Endpoints

Verifies the /api/knowledge endpoints using FastAPI TestClient.
"""
import unittest
from unittest.mock import MagicMock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from sros.nexus.api.server import app

class TestKnowledgeAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        
        # Mock Kernel Context
        self.mock_kernel = MagicMock()
        self.mock_kernel.memory = MagicMock()
        self.mock_kernel.registry = MagicMock()
        
        # Mock Codex
        self.mock_codex = MagicMock()
        self.mock_kernel.memory.codex = self.mock_codex
        
        # Inject into app state
        app.state.kernel = self.mock_kernel
        
    def test_list_packs(self):
        print("\n--- Testing List Knowledge Packs ---")
        
        # Setup mock return
        self.mock_codex.list_packs.return_value = ["pack1", "pack2"]
        
        response = self.client.get("/api/knowledge/packs")
        print(f"Response: {response.json()}")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["count"], 2)
        self.assertEqual(data["packs"], ["pack1", "pack2"])
        
    def test_search_knowledge(self):
        print("\n--- Testing Search Knowledge ---")
        
        # Setup mock return
        mock_pack = MagicMock()
        mock_pack.to_dict.return_value = {"id": "p1", "name": "Test Pack"}
        self.mock_codex.search_packs.return_value = [mock_pack]
        
        response = self.client.get("/api/knowledge/search?query=test")
        print(f"Response: {response.json()}")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["name"], "Test Pack")
        
    def test_status_daemons(self):
        print("\n--- Testing Status API (Daemons) ---")
        
        self.mock_kernel.registry.running = {"daemon1": True, "daemon2": False}
        
        response = self.client.get("/api/status")
        print(f"Response: {response.json()}")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("daemons", data)
        self.assertEqual(data["daemons"]["daemon1"], True)

if __name__ == '__main__':
    unittest.main()
