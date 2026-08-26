import json

from scripts.lab2_check import evaluate


def manifest():
    return {
        "id": "LAB-2", "objective": "calibration",
        "execution": {"initial_repetitions_per_case": 3, "active_target_repetitions_per_case": 3, "maximum_repetitions_per_case": 5},
        "gates": {"minimum_pipeline_completion_rate": 0.80, "minimum_case_pass_rate": 0.80, "minimum_group_pass_rate": 0.80},
        "cases": [{"id": "C1", "group": "true", "hypothesis": "fait", "accepted_verdicts": ["CONFIRMED"], "minimum_confidence": 0.9}],
    }


def record(status="COMPLETED", verdict="CONFIRMED", confidence=0.95, objective="calibration"):
    return {"status": status, "question": "fait", "objective": objective, "machine_judgment": {"verdict": verdict, "confidence": confidence} if status == "COMPLETED" else None}


def test_incomplete_campaign_is_pending():
    result = evaluate(manifest(), [record(), record()])
    assert result["status"] == "PENDING"
    assert result["cases"][0]["remaining_initial"] == 1


def test_complete_correct_tranche_passes():
    result = evaluate(manifest(), [record(), record(), record()])
    assert result["status"] == "PASS"


def test_failure_counts_against_availability_not_as_verdict():
    result = evaluate(manifest(), [record(), record(), record(status="FAILED")])
    assert result["status"] == "FAIL"
    assert result["cases"][0]["completed"] == 2
    assert result["cases"][0]["passed"] == 2


def test_unrelated_research_record_is_ignored():
    result = evaluate(manifest(), [record(objective="research")])
    assert result["matched_runs"] == 0
