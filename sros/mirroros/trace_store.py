from typing import List, Dict, Any
import json
import os
import time


class TraceStore:
    """
    Stores execution traces.
    """

    def __init__(self, storage_path: str = "./data/traces"):
        self.storage_path = storage_path
        self.traces: List[Dict[str, Any]] = []

        if storage_path.endswith('.jsonl'):
            dir_path = os.path.dirname(storage_path)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
        elif not os.path.exists(storage_path):
            os.makedirs(storage_path, exist_ok=True)

    def _normalize_event(self, trace_event: Dict[str, Any]) -> Dict[str, Any]:
        payload = trace_event.get("payload") or {}
        event_type = trace_event.get("event_type", "unknown")
        topic = trace_event.get("topic") or event_type.split(".", 1)[0]
        run_id = trace_event.get("run_id") or payload.get("run_id")

        return {
            "event_id": trace_event.get("event_id"),
            "timestamp": float(trace_event.get("timestamp", time.time())),
            "event_type": event_type,
            "source": trace_event.get("source", "runtime"),
            "topic": topic,
            "run_id": run_id,
            "correlation_id": trace_event.get("correlation_id"),
            "payload": payload,
        }

    def _resolved_path(self) -> str:
        if self.storage_path.endswith('.jsonl'):
            return self.storage_path
        filename = f"trace_{int(time.time() // 3600)}.jsonl"
        return os.path.join(self.storage_path, filename)

    def append(self, trace_event: Dict[str, Any]):
        """
        Append a trace event.
        """
        normalized = self._normalize_event(trace_event)
        self.traces.append(normalized)

        filepath = self._resolved_path()
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(normalized, sort_keys=True) + "\n")

    def load_recent(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Load the most recent traces.
        """
        return self.traces[-count:]

    def load_from_disk(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Load recent traces from disk in deterministic order."""
        files: List[str] = []
        if self.storage_path.endswith('.jsonl'):
            if os.path.exists(self.storage_path):
                files = [self.storage_path]
        elif os.path.exists(self.storage_path):
            files = sorted(
                os.path.join(self.storage_path, name)
                for name in os.listdir(self.storage_path)
                if name.endswith('.jsonl')
            )

        loaded: List[Dict[str, Any]] = []
        for file_path in files:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    loaded.append(self._normalize_event(json.loads(line)))

        if limit <= 0:
            return loaded
        return loaded[-limit:]

    def summarize(self, count: int = 100) -> Dict[str, Any]:
        """Return a deterministic summary for assertions and runtime checks."""
        events = self.load_recent(count) if self.traces else self.load_from_disk(limit=count)
        by_type: Dict[str, int] = {}
        run_ids = set()

        for event in events:
            event_type = event["event_type"]
            by_type[event_type] = by_type.get(event_type, 0) + 1
            if event.get("run_id"):
                run_ids.add(event["run_id"])

        return {
            "total_events": len(events),
            "event_types": dict(sorted(by_type.items())),
            "run_ids": sorted(run_ids),
        }
