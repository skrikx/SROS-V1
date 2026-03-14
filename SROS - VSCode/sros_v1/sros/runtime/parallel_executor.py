"""
Parallel Executor
=================

ASI Speed Layer: Parallel Task Execution.
"""
import concurrent.futures
import logging
from typing import List, Callable, Any

logger = logging.getLogger(__name__)

class ParallelExecutor:
    """
    Executes tasks in parallel using a thread pool.
    """
    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)

    def execute(self, tasks: List[Callable[[], Any]]) -> List[Any]:
        """
        Execute a list of callables in parallel.
        """
        futures = [self.executor.submit(task) for task in tasks]
        results = []
        for future in concurrent.futures.as_completed(futures):
            try:
                results.append(future.result())
            except Exception as e:
                logger.error(f"Parallel execution error: {e}")
                results.append(None)
        return results

    def map(self, func: Callable[[Any], Any], items: List[Any]) -> List[Any]:
        """
        Map a function over a list of items in parallel.
        """
        return list(self.executor.map(func, items))
