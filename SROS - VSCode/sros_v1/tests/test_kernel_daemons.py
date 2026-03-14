"""
Integration Tests: Kernel Daemons (Scheduler + Health)

Tests that scheduler and health daemons work correctly and integrate
with the kernel bootstrap and event bus.

This validates Objective O2 foundation: "Observable daemon self-scheduling"
"""
import pytest
import time
import threading
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta

from sros.kernel.event_bus import EventBus
from sros.kernel.daemons.scheduler_daemon import SchedulerDaemon, ScheduledTask
from sros.kernel.daemons.health_daemon import HealthDaemon, HealthStatus
from sros.kernel.kernel_bootstrap import boot


class TestSchedulerDaemon:
    """Test suite for Scheduler Daemon."""
    
    @pytest.fixture
    def event_bus(self):
        """Create fresh event bus."""
        return EventBus()
    
    @pytest.fixture
    def scheduler(self, event_bus):
        """Create scheduler daemon."""
        return SchedulerDaemon(event_bus, check_interval=0.05)
    
    def test_scheduler_initializes(self, scheduler, event_bus):
        """Verify scheduler daemon initializes correctly."""
        assert scheduler.running is False
        assert scheduler.check_interval == 0.05
        assert len(scheduler.tasks) == 0
    
    def test_scheduler_register_task(self, scheduler, event_bus):
        """Verify scheduler can register tasks."""
        callback = Mock()
        
        result = scheduler.register_task("test_task", callback, 1.0)
        
        assert result is True
        assert "test_task" in scheduler.tasks
        assert scheduler.tasks["test_task"].interval == 1.0
    
    def test_scheduler_register_duplicate_task(self, scheduler):
        """Verify scheduler rejects duplicate task names."""
        callback = Mock()
        
        scheduler.register_task("test_task", callback, 1.0)
        result = scheduler.register_task("test_task", callback, 2.0)
        
        assert result is False
    
    def test_scheduler_unregister_task(self, scheduler):
        """Verify scheduler can unregister tasks."""
        callback = Mock()
        scheduler.register_task("test_task", callback, 1.0)
        
        result = scheduler.unregister_task("test_task")
        
        assert result is True
        assert "test_task" not in scheduler.tasks
    
    def test_scheduler_enable_disable_task(self, scheduler):
        """Verify scheduler can enable/disable tasks."""
        callback = Mock()
        scheduler.register_task("test_task", callback, 1.0)
        
        # Disable
        assert scheduler.disable_task("test_task") is True
        assert scheduler.tasks["test_task"].enabled is False
        
        # Enable
        assert scheduler.enable_task("test_task") is True
        assert scheduler.tasks["test_task"].enabled is True
    
    def test_scheduler_start_stop(self, scheduler, event_bus):
        """Verify scheduler starts and stops correctly."""
        events_published = []
        
        def capture_event(event_type, payload):
            events_published.append((event_type, payload))
        
        event_bus.subscribe("scheduler.started", capture_event)
        event_bus.subscribe("scheduler.stopped", capture_event)
        
        scheduler.start()
        assert scheduler.running is True
        assert scheduler._thread is not None
        
        time.sleep(0.1)  # Let it run a bit
        
        scheduler.stop()
        assert scheduler.running is False
    
    def test_scheduler_executes_task(self, scheduler, event_bus):
        """Verify scheduler executes registered tasks."""
        execution_count = [0]
        
        def task_callback():
            execution_count[0] += 1
        
        events_captured = []
        
        def capture_event(payload):
            events_captured.append(payload)
        
        event_bus.subscribe("scheduler.task_executed", capture_event)
        
        # Register task with 0.1s interval
        scheduler.register_task("fast_task", task_callback, 0.1)
        scheduler.start()
        
        # Let scheduler run and execute task multiple times
        time.sleep(0.5)
        
        scheduler.stop()
        
        # Should have executed at least once
        assert execution_count[0] >= 1
        assert len(events_captured) >= 1
    
    def test_scheduler_task_error_handling(self, scheduler, event_bus):
        """Verify scheduler handles task errors gracefully."""
        def failing_callback():
            raise ValueError("Task failed")
        
        events_captured = []
        
        def capture_event(payload):
            events_captured.append(payload)
        
        event_bus.subscribe("scheduler.task_error", capture_event)
        
        scheduler.register_task("failing_task", failing_callback, 0.1)
        scheduler.start()
        
        time.sleep(0.3)
        
        scheduler.stop()
        
        # Should have captured error events
        assert len(events_captured) >= 1
        
        # Check that error_count was incremented
        task_status = scheduler.get_task_status("failing_task")
        assert task_status["error_count"] >= 1
    
    def test_scheduler_get_task_status(self, scheduler):
        """Verify scheduler reports task status correctly."""
        callback = Mock()
        scheduler.register_task("status_task", callback, 2.0)
        
        status = scheduler.get_task_status("status_task")
        
        assert status is not None
        assert status["name"] == "status_task"
        assert status["interval"] == 2.0
        assert status["enabled"] is True
        assert status["run_count"] == 0
    
    def test_scheduler_get_all_tasks_status(self, scheduler):
        """Verify scheduler reports all tasks status."""
        callback = Mock()
        scheduler.register_task("task1", callback, 1.0)
        scheduler.register_task("task2", callback, 2.0)
        
        status = scheduler.get_all_tasks_status()
        
        assert len(status) == 2
        assert "task1" in status
        assert "task2" in status


class TestHealthDaemon:
    """Test suite for Health Daemon."""
    
    @pytest.fixture
    def event_bus(self):
        """Create fresh event bus."""
        return EventBus()
    
    @pytest.fixture
    def health_daemon(self, event_bus):
        """Create health daemon."""
        return HealthDaemon(event_bus, check_interval=0.05)
    
    def test_health_daemon_initializes(self, health_daemon):
        """Verify health daemon initializes correctly."""
        assert health_daemon.running is False
        assert health_daemon.check_interval == 0.05
        assert len(health_daemon.health_checks) == 0
    
    def test_health_daemon_register_check(self, health_daemon):
        """Verify health daemon can register health checks."""
        check_callback = Mock(return_value=True)
        
        result = health_daemon.register_health_check("runtime", check_callback)
        
        assert result is True
        assert "runtime" in health_daemon.health_checks
    
    def test_health_daemon_register_duplicate_check(self, health_daemon):
        """Verify health daemon rejects duplicate plane names."""
        check_callback = Mock(return_value=True)
        
        health_daemon.register_health_check("runtime", check_callback)
        result = health_daemon.register_health_check("runtime", check_callback)
        
        assert result is False
    
    def test_health_daemon_unregister_check(self, health_daemon):
        """Verify health daemon can unregister health checks."""
        check_callback = Mock(return_value=True)
        health_daemon.register_health_check("runtime", check_callback)
        
        result = health_daemon.unregister_health_check("runtime")
        
        assert result is True
        assert "runtime" not in health_daemon.health_checks
    
    def test_health_daemon_start_stop(self, health_daemon, event_bus):
        """Verify health daemon starts and stops correctly."""
        events_published = []
        
        def capture_event(event_type, payload):
            events_published.append((event_type, payload))
        
        event_bus.subscribe("health.started", capture_event)
        event_bus.subscribe("health.stopped", capture_event)
        
        health_daemon.start()
        assert health_daemon.running is True
        
        time.sleep(0.1)
        
        health_daemon.stop()
        assert health_daemon.running is False
    
    def test_health_daemon_checks_plane_health(self, health_daemon, event_bus):
        """Verify health daemon checks registered plane health."""
        check_callback = Mock(return_value=True)
        events_captured = []
        
        def capture_event(payload):
            events_captured.append(payload)
        
        event_bus.subscribe("health.status", capture_event)
        
        health_daemon.register_health_check("runtime", check_callback)
        health_daemon.start()
        
        time.sleep(0.3)
        
        health_daemon.stop()
        
        # Should have published health status events
        assert len(events_captured) >= 1
        
        # Verify callback was called
        assert check_callback.call_count >= 1
    
    def test_health_daemon_detects_unhealthy_plane(self, health_daemon, event_bus):
        """Verify health daemon detects unhealthy planes."""
        check_callback = Mock(return_value=False)  # Return False = unhealthy
        degraded_events = []
        
        def capture_event(event_type, payload):
            degraded_events.append((event_type, payload))
        
        event_bus.subscribe("health.degraded", capture_event)
        
        health_daemon.register_health_check("runtime", check_callback)
        health_daemon.start()
        
        # Let it run and detect the unhealthy status
        time.sleep(0.3)
        
        health_daemon.stop()
        
        # Verify status changed to unhealthy
        status = health_daemon.get_plane_status("runtime")
        assert status["status"] == HealthStatus.UNHEALTHY
    
    def test_health_daemon_detects_recovery(self, health_daemon, event_bus):
        """Verify health daemon detects plane recovery."""
        # Start unhealthy
        check_callback = Mock(return_value=False)
        recovered_events = []
        
        def capture_event(payload):
            recovered_events.append(payload)
        
        event_bus.subscribe("health.recovered", capture_event)
        
        health_daemon.register_health_check("runtime", check_callback)
        health_daemon.start()
        
        time.sleep(0.3)
        
        # Change to healthy
        check_callback.return_value = True
        
        time.sleep(0.3)
        
        health_daemon.stop()
        
        # Should have detected recovery
        assert len(recovered_events) >= 1
    
    def test_health_daemon_get_plane_status(self, health_daemon):
        """Verify health daemon reports plane status."""
        check_callback = Mock(return_value=True)
        health_daemon.register_health_check("runtime", check_callback)
        
        status = health_daemon.get_plane_status("runtime")
        
        assert status is not None
        assert status["plane"] == "runtime"
        assert status["status"] == HealthStatus.UNKNOWN  # Before first check
    
    def test_health_daemon_get_all_planes_status(self, health_daemon):
        """Verify health daemon reports all planes status."""
        callback1 = Mock(return_value=True)
        callback2 = Mock(return_value=False)
        
        health_daemon.register_health_check("runtime", callback1)
        health_daemon.register_health_check("governance", callback2)
        
        status = health_daemon.get_all_planes_status()
        
        assert len(status) == 2
        assert "runtime" in status
        assert "governance" in status


class TestDaemonIntegration:
    """Integration tests for daemons with kernel bootstrap."""
    
    def test_kernel_boot_with_daemons(self):
        """Verify kernel boots with all daemons."""
        ctx = boot()
        
        assert ctx is not None
        assert ctx.event_bus is not None
        assert ctx.registry is not None
        
        # Verify daemons are registered
        assert "heartbeat" in ctx.registry.daemons
        assert "scheduler" in ctx.registry.daemons
        assert "health" in ctx.registry.daemons
    
    def test_daemons_start_on_boot(self):
        """Verify daemons start on kernel boot."""
        ctx = boot()
        
        time.sleep(0.1)
        
        # Verify daemons are running
        assert ctx.registry.running["heartbeat"] is True
        assert ctx.registry.running["scheduler"] is True
        assert ctx.registry.running["health"] is True
        
        # Clean up
        ctx.registry.stop_all()
    
    def test_heartbeat_daemon_publishes_events(self):
        """Verify heartbeat daemon publishes heartbeat events."""
        ctx = boot()
        
        heartbeat_events = []
        
        def capture_heartbeat(payload):
            heartbeat_events.append(payload)
        
        ctx.event_bus.subscribe("kernel.heartbeat", capture_heartbeat)
        
        time.sleep(1.5)  # Let heartbeat run (interval is 1s)
        
        assert len(heartbeat_events) >= 1
        
        ctx.registry.stop_all()
    
    def test_scheduler_daemon_in_kernel(self):
        """Verify scheduler daemon is accessible from kernel context."""
        ctx = boot()
        
        scheduler = ctx.registry.daemons.get("scheduler")
        assert scheduler is not None
        assert isinstance(scheduler, SchedulerDaemon)
        
        # Register a task
        callback = Mock()
        scheduler.register_task("kernel_task", callback, 0.1)
        
        time.sleep(0.3)
        
        # Task should have executed
        assert callback.call_count >= 1
        
        ctx.registry.stop_all()
    
    def test_health_daemon_in_kernel(self):
        """Verify health daemon is accessible from kernel context."""
        ctx = boot()
        
        health = ctx.registry.daemons.get("health")
        assert health is not None
        assert isinstance(health, HealthDaemon)
        
        # Register a plane health check
        check_callback = Mock(return_value=True)
        result = health.register_health_check("test_plane", check_callback)
        
        # Verify it was registered
        assert result is True
        assert "test_plane" in health.health_checks
        
        ctx.registry.stop_all()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
