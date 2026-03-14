"""
Scheduler Daemon

Executes scheduled tasks at specified intervals.
Maintains a priority queue of tasks and manages their execution.
"""
import time
import threading
import logging
from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import heapq

logger = logging.getLogger(__name__)


@dataclass
class ScheduledTask:
    """Represents a scheduled task."""
    name: str
    interval: float  # seconds
    callback: Callable
    last_run: Optional[datetime] = None
    next_run: datetime = field(default_factory=datetime.now)
    enabled: bool = True
    run_count: int = 0
    error_count: int = 0
    
    def __lt__(self, other):
        """Comparison for heap queue (by next_run time)."""
        return self.next_run < other.next_run
    
    def should_run(self) -> bool:
        """Check if task should run now."""
        return self.enabled and datetime.now() >= self.next_run
    
    def mark_run(self, success: bool = True):
        """Update task after execution."""
        self.last_run = datetime.now()
        self.run_count += 1
        if not success:
            self.error_count += 1
        self.next_run = datetime.now() + timedelta(seconds=self.interval)


class SchedulerDaemon:
    """
    Scheduler Daemon - Execute periodic tasks.
    
    Features:
    - Register tasks with intervals (in seconds)
    - Priority queue execution (earliest first)
    - Error tracking and recovery
    - Enable/disable tasks at runtime
    - Event bus integration for observability
    """
    
    def __init__(self, event_bus, check_interval: float = 0.1):
        """
        Initialize scheduler.
        
        Args:
            event_bus: Event bus for publishing events
            check_interval: How often to check for runnable tasks (seconds)
        """
        self.event_bus = event_bus
        self.check_interval = check_interval
        self.running = False
        self._thread = None
        self.tasks: Dict[str, ScheduledTask] = {}
        self._task_queue = []
        self._lock = threading.RLock()
    
    def register_task(
        self,
        name: str,
        callback: Callable,
        interval: float
    ) -> bool:
        """
        Register a task to run at specified interval.
        
        Args:
            name: Unique task name
            callback: Callable to execute (should accept no args)
            interval: Interval in seconds
        
        Returns:
            True if registered, False if name already exists
        """
        with self._lock:
            if name in self.tasks:
                logger.warning(f"Task '{name}' already registered")
                return False
            
            task = ScheduledTask(
                name=name,
                interval=interval,
                callback=callback,
                next_run=datetime.now() + timedelta(seconds=interval)
            )
            self.tasks[name] = task
            heapq.heappush(self._task_queue, task)
            
            logger.info(f"Registered task '{name}' with interval {interval}s")
            self.event_bus.publish(
                "kernel",
                "scheduler.task_registered",
                {"name": name, "interval": interval}
            )
            return True
    
    def unregister_task(self, name: str) -> bool:
        """
        Unregister a task.
        
        Args:
            name: Task name
        
        Returns:
            True if unregistered, False if not found
        """
        with self._lock:
            if name not in self.tasks:
                logger.warning(f"Task '{name}' not found")
                return False
            
            del self.tasks[name]
            logger.info(f"Unregistered task '{name}'")
            self.event_bus.publish(
                "kernel",
                "scheduler.task_unregistered",
                {"name": name}
            )
            return True
    
    def enable_task(self, name: str) -> bool:
        """Enable a disabled task."""
        with self._lock:
            if name not in self.tasks:
                return False
            self.tasks[name].enabled = True
            logger.info(f"Enabled task '{name}'")
            return True
    
    def disable_task(self, name: str) -> bool:
        """Disable a task (won't run)."""
        with self._lock:
            if name not in self.tasks:
                return False
            self.tasks[name].enabled = False
            logger.info(f"Disabled task '{name}'")
            return True
    
    def get_task_status(self, name: str) -> Optional[Dict[str, Any]]:
        """Get status of a task."""
        with self._lock:
            if name not in self.tasks:
                return None
            
            task = self.tasks[name]
            return {
                "name": task.name,
                "interval": task.interval,
                "enabled": task.enabled,
                "run_count": task.run_count,
                "error_count": task.error_count,
                "last_run": task.last_run.isoformat() if task.last_run else None,
                "next_run": task.next_run.isoformat()
            }
    
    def get_all_tasks_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all tasks."""
        with self._lock:
            return {
                name: {
                    "name": task.name,
                    "interval": task.interval,
                    "enabled": task.enabled,
                    "run_count": task.run_count,
                    "error_count": task.error_count,
                    "last_run": task.last_run.isoformat() if task.last_run else None,
                    "next_run": task.next_run.isoformat()
                }
                for name, task in self.tasks.items()
            }
    
    def start(self):
        """Start the scheduler daemon."""
        if self.running:
            logger.warning("Scheduler already running")
            return
        
        self.running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        
        logger.info("Scheduler daemon started")
        self.event_bus.publish(
            "kernel",
            "scheduler.started",
            {"task_count": len(self.tasks)}
        )
    
    def stop(self):
        """Stop the scheduler daemon."""
        if not self.running:
            return
        
        self.running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        
        logger.info("Scheduler daemon stopped")
        self.event_bus.publish(
            "kernel",
            "scheduler.stopped",
            {"tasks_executed": sum(t.run_count for t in self.tasks.values())}
        )
    
    def _loop(self):
        """Main scheduler loop."""
        while self.running:
            try:
                self._check_and_execute_tasks()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                self.event_bus.publish(
                    "kernel",
                    "scheduler.error",
                    {"error": str(e)}
                )
    
    def _check_and_execute_tasks(self):
        """Check for runnable tasks and execute them."""
        with self._lock:
            # Rebuild queue from current tasks
            self._task_queue = list(self.tasks.values())
            heapq.heapify(self._task_queue)
        
        while True:
            with self._lock:
                if not self._task_queue:
                    break
                
                task = self._task_queue[0]
                
                if not task.should_run():
                    break
                
                heapq.heappop(self._task_queue)
            
            # Execute outside lock to prevent blocking
            try:
                logger.debug(f"Executing task '{task.name}'")
                task.callback()
                task.mark_run(success=True)
                
                self.event_bus.publish(
                    "kernel",
                    "scheduler.task_executed",
                    {
                        "name": task.name,
                        "run_count": task.run_count,
                        "error_count": task.error_count
                    }
                )
            except Exception as e:
                logger.error(f"Error executing task '{task.name}': {e}")
                task.mark_run(success=False)
                
                self.event_bus.publish(
                    "kernel",
                    "scheduler.task_error",
                    {"name": task.name, "error": str(e)}
                )
            
            # Re-enqueue task
            with self._lock:
                heapq.heappush(self._task_queue, task)
