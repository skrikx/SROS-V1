"""
Batch Processor
===============

ASI Speed Layer: Batch Task Processing.
"""
import logging
from typing import List, Any, Callable

logger = logging.getLogger(__name__)

class BatchProcessor:
    """
    Processes items in batches to optimize throughput.
    """
    def __init__(self, batch_size: int = 5):
        self.batch_size = batch_size

    def process(self, items: List[Any], processor: Callable[[List[Any]], List[Any]]) -> List[Any]:
        """
        Process items in batches using the provided processor function.
        """
        results = []
        for i in range(0, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]
            try:
                batch_results = processor(batch)
                results.extend(batch_results)
            except Exception as e:
                logger.error(f"Batch processing error: {e}")
                # Fallback: process individually or return errors
                results.extend([None] * len(batch))
        return results
