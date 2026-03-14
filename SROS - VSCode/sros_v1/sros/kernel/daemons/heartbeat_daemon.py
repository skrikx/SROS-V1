
import time
import threading
from sros.kernel.event_bus import EventBus

class HeartbeatDaemon:
    def __init__(self, event_bus: EventBus, interval: int = 1):
        self.event_bus = event_bus
        self.interval = interval
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)

    def _loop(self):
        while self.running:
            self.event_bus.publish("kernel", "kernel.heartbeat", {"timestamp": time.time()})
            time.sleep(self.interval)