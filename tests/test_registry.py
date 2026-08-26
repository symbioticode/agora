from datetime import datetime, timezone

from agora.registry import ExperimentRegistry
from tests.test_engine import FakeGateway
from agora.engine import DebateEngine


def test_registry_ids_persistence_and_markdown(tmp_path):
    registry = ExperimentRegistry(tmp_path / "experiments")
    debate = DebateEngine(FakeGateway()).run("La Terre tourne autour du Soleil")
    first = registry.create(debate, {"title": "Rotation terrestre"}, datetime(2026, 8, 26, tzinfo=timezone.utc))
    second = registry.create(debate, now=datetime(2026, 8, 26, 1, tzinfo=timezone.utc))
    assert first["id"] == "AGO-EXP-2026-0001"
    assert second["id"] == "AGO-EXP-2026-0002"
    assert registry.get(first["id"])["evidence_sha256"] == first["evidence_sha256"]
    assert "AGO-EXP-2026-0001" in registry.markdown(first)
    assert first["evidence_sha256"] in registry.markdown(first)


def test_supervisor_observation_is_append_only_event(tmp_path):
    registry = ExperimentRegistry(tmp_path / "experiments")
    debate = DebateEngine(FakeGateway()).run("Question")
    record = registry.create(debate)
    original_transcript = record["observation"]["transcript"]
    updated = registry.add_observation(record["id"], "andrei", "À revoir.")
    assert updated["observation"]["transcript"] == original_transcript
    assert updated["supervisor_observations"][0]["content"] == "À revoir."


def test_failed_experiment_is_durable_and_exportable(tmp_path):
    registry = ExperimentRegistry(tmp_path / "experiments")
    experiment_id = registry.reserve_id(datetime(2026, 8, 26, tzinfo=timezone.utc))
    failed = registry.create_failed(experiment_id, {"question": "Question"}, [{"round": 0, "agent": "A", "content": "Partiel"}], {"code": "ProviderError", "message": "Réponse vide"}, datetime(2026, 8, 26, tzinfo=timezone.utc))
    assert registry.get(experiment_id)["status"] == "FAILED"
    assert "Aucun verdict produit" in registry.markdown(failed)
