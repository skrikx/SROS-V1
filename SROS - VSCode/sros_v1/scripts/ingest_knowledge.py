"""
Ingest Knowledge Script

Ingests the Master SROS Schemas from the Knowledge directory into the SROS Codex Memory.
"""
import sys
import os
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sros.srxml.loader import SRXMLLoader
from sros.memory.codex_memory import CodexMemory, KnowledgePack

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("IngestKnowledge")

def main():
    # Paths
    # Assuming script is run from project root or scripts dir
    # We need to find the 'Knowledge' directory which is a sibling of 'sros_v1' or inside 'SROS - VSCode'
    
    # Current layout based on user info:
    # c:\Users\hassm\OneDrive\Desktop\SROS\SROS - VSCode\sros_v1\scripts\ingest_knowledge.py
    # c:\Users\hassm\OneDrive\Desktop\SROS\SROS - VSCode\Knowledge
    
    base_dir = Path(__file__).parent.parent.parent # SROS - VSCode
    knowledge_dir = base_dir / "Knowledge" / "Master_SROS_Schemas"
    
    if not knowledge_dir.exists():
        # Fallback for different repo structure
        knowledge_dir = Path("C:/Users/hassm/OneDrive/Desktop/SROS/SROS - VSCode/Knowledge/Master_SROS_Schemas")
    
    if not knowledge_dir.exists():
        logger.error(f"Knowledge directory not found at: {knowledge_dir}")
        return

    logger.info(f"Scanning for schemas in: {knowledge_dir}")
    
    # Load Schemas
    loader = SRXMLLoader()
    schemas = loader.load_directory(str(knowledge_dir))
    
    if not schemas:
        logger.warning("No schemas found.")
        return
        
    logger.info(f"Found {len(schemas)} schemas.")
    
    # Initialize Codex
    codex = CodexMemory()
    
    # Ingest
    for schema in schemas:
        schema_id = schema.get('@id')
        if not schema_id:
            schema_id = Path(schema['_filename']).stem
            
        name = f"Schema: {schema_id}"
        
        # Create Pack
        pack = KnowledgePack(
            pack_id=f"schema.{schema_id}",
            name=name,
            content=schema
        )
        pack.metadata = {
            "type": "srxml_schema",
            "source": schema.get('_source_file'),
            "ingested_at": "now" # In real app use timestamp
        }
        
        codex.add_pack(pack)
        logger.info(f"Ingested: {name}")
        
    logger.info("Ingestion complete.")
    
    # Verify
    stats = codex.get_stats()
    logger.info(f"Codex Stats: {stats}")

if __name__ == "__main__":
    main()
