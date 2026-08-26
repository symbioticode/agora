from datetime import datetime, timezone

from agora.engine import DebateEngine
from agora.registry import ExperimentRegistry
from scripts.project_kbm import project
from tests.test_engine import FakeGateway


def test_projection_is_deterministic_and_idempotent(tmp_path):
    source = tmp_path / "experiments"
    destination = tmp_path / "projection"
    registry = ExperimentRegistry(source)
    record = registry.create(
        DebateEngine(FakeGateway()).run("Question simple"),
        now=datetime(2026, 8, 26, tzinfo=timezone.utc),
    )
    first = project(source, destination, datetime(2026, 8, 26, 1, tzinfo=timezone.utc))
    second = project(source, destination, datetime(2026, 8, 26, 2, tzinfo=timezone.utc))
    assert first["entries"][0]["status"] == "NEW"
    assert second["entries"][0]["status"] == "UNCHANGED"
    article = (destination / f"{record['id']}.md").read_text(encoding="utf-8")
    assert record["record_sha256"] in article
    assert "home-kbm" in second["destination"]


def test_projection_refuses_modified_record(tmp_path):
    source = tmp_path / "experiments"
    registry = ExperimentRegistry(source)
    record = registry.create(DebateEngine(FakeGateway()).run("Question"))
    path = next(source.glob("*/AGO-EXP-*.json"))
    record["question"] = "Modification non scellée"
    registry._atomic_write(path, record)
    manifest = project(source, tmp_path / "projection")
    assert manifest["status"] == "PARTIAL"
    assert manifest["entries"][0]["reason"] == "HASH_MISMATCH"


def test_failed_experiment_is_projected_as_research_evidence(tmp_path):
    source = tmp_path / "experiments"
    registry = ExperimentRegistry(source)
    experiment_id = registry.reserve_id(datetime(2026, 8, 26, tzinfo=timezone.utc))
    registry.create_failed(experiment_id, {"question": "Question"}, [], {"code": "ProviderError", "message": "vide"}, datetime(2026, 8, 26, tzinfo=timezone.utc))
    manifest = project(source, tmp_path / "projection")
    assert manifest["status"] == "SUCCESS"
    article = (tmp_path / "projection" / f"{experiment_id}.md").read_text(encoding="utf-8")
    assert "expérience interrompue" in article
