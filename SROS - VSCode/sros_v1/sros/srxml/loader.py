"""
SRXML Loader

Utilities for batch loading and validating SRXML files from directories.
"""
import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from .parser import SRXMLParser

logger = logging.getLogger(__name__)

class SRXMLLoader:
    """
    Loads SRXML files from file system.
    """
    
    def __init__(self):
        self.parser = SRXMLParser()
        
    def load_directory(self, directory_path: str, recursive: bool = False) -> List[Dict[str, Any]]:
        """
        Load all .xml files from a directory.
        
        Args:
            directory_path: Path to directory
            recursive: Whether to search recursively
            
        Returns:
            List of parsed SRXML dictionaries
        """
        results = []
        path = Path(directory_path)
        
        if not path.exists():
            logger.warning(f"Directory not found: {directory_path}")
            return []
            
        pattern = "**/*.xml" if recursive else "*.xml"
        
        for file_path in path.glob(pattern):
            try:
                data = self.parser.parse(str(file_path))
                # Inject source path for reference
                data['_source_file'] = str(file_path)
                data['_filename'] = file_path.name
                results.append(data)
                logger.debug(f"Loaded SRXML: {file_path.name}")
            except Exception as e:
                logger.error(f"Failed to load {file_path}: {e}")
                
        return results

    def load_schema_pack(self, directory_path: str) -> Dict[str, Any]:
        """
        Load a directory as a schema pack.
        
        Returns a dict keyed by schema ID (or filename if ID missing).
        """
        items = self.load_directory(directory_path)
        pack = {}
        
        for item in items:
            # Try to find an ID, otherwise use filename
            item_id = item.get('@id')
            if not item_id:
                # Fallback to filename without extension
                item_id = Path(item['_filename']).stem
                
            pack[item_id] = item
            
        return pack
