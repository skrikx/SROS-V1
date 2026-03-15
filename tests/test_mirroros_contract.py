import json

from sros.mirroros.trace_store import TraceStore
from sros.mirroros.witness import Witness
from sros.mirroros.drift_detector import DriftDetector


def test_witness_records_canonical_event_contract(tmp_path):
    store = TraceStore(storage_path=str(tmp_path / "traces.jsonl"))
    witness = Witness(store)

    witness.record(
        "workflow.start",
        {"workflow_id": "wf-1", "run_id": "run-123"},
        source="test_runner",
        topic="workflow",
        run_id="run-123",
        correlation_id="corr-1",
    )

    event = store.load_recent(1)[0]
    assert event["event_type"] == "workflow.start"
    assert event["source"] == "test_runner"
    assert event["topic"] == "workflow"
    assert event["run_id"] == "run-123"
    assert event["correlation_id"] == "corr-1"
    assert isinstance(event["payload"], dict)
    assert "event_id" in event


def test_trace_store_summary_and_disk_loading(tmp_path):
    store_path = tmp_path / "traces.jsonl"
    store = TraceStore(storage_path=str(store_path))
    witness = Witness(store)

    witness.record("workflow.start", {"run_id": "run-1"}, run_id="run-1")
    witness.record("workflow.end", {"run_id": "run-1"}, run_id="run-1")

    summary = store.summarize()
    assert summary["total_events"] == 2
    assert summary["event_types"]["workflow.end"] == 1
    assert summary["run_ids"] == ["run-1"]

    disk_events = store.load_from_disk(limit=10)
    assert len(disk_events) == 2
    json.loads(store_path.read_text(encoding="utf-8").splitlines()[0])


def test_drift_report_is_metric_threshold_truthful():
    detector = DriftDetector({"performance_threshold": 0.10})
    detector.record_metric("agent.architect", "latency", 10.0)
    detector.record_metric("agent.architect", "latency", 12.0)

    report = detector.get_drift_report()
    assert report["detector_type"] == "metric_threshold"
    assert report["threshold_breaches"] >= 1
