"""
Test Knowledge Ingestion

Verifies that SRXML schemas have been correctly ingested into Codex Memory.
"""
import unittest
import sys
import os
import shutil
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sros.memory.codex_memory import CodexMemory

class TestKnowledgeIngestion(unittest.TestCase):
    def test_schemas_exist(self):
        print("\n--- Testing Codex Memory Content ---")
        
        # Initialize Codex (it loads from disk)
        codex = CodexMemory()
        
        # List packs
        packs = codex.list_packs()
        print(f"Found {len(packs)} packs: {packs}")
        
        # Check for specific schemas we expect
        # IDs based on filenames or @id attributes in the XMLs
        expected_schemas = [
            "schema.SROS.OS.Master.Schema.v1",
            "schema.MirrorOS.Master.Schema.v1",
            "schema.SRX.Runtime.Master.Schema.v1"
        ]
        
        found_count = 0
        for schema_id in expected_schemas:
            pack = codex.get_pack(schema_id)
            if pack:
                print(f"✓ Found {schema_id}")
                found_count += 1
                # Verify content structure
                self.assertIsInstance(pack.content, dict)
                self.assertTrue(len(pack.content) > 0)
            else:
                print(f"✗ Missing {schema_id}")
                
        # We expect at least some schemas to be found
        self.assertTrue(found_count > 0, "No expected schemas found in Codex")
        
        # Test Search
        print("Testing search for 'mirroros'...")
        results = codex.search_packs("mirroros")
        print(f"Found {len(results)} matches")
        self.assertTrue(len(results) > 0)

if __name__ == '__main__':
    unittest.main()
