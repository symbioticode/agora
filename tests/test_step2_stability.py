from copy import deepcopy

import pytest

from scripts.step2_stability import DEFAULT_JUDGES, analyze, prepare_manifest


def judgment(manifest, hypothesis_id, judge, repeat, verdict="NUANCED"):
    return {
        "hypothesis_id": hypothesis_id,
        "judge": judge,
        "repeat": repeat,
        "transcript_sha256": manifest["hypotheses"][hypothesis_id]["transcript_sha256"],
        "verdict": verdict,
        "confidence": 0.75,
    }


def complete_set(manifest):
    return [
        judgment(manifest, hypothesis_id, judge, repeat)
        for hypothesis_id in manifest["hypotheses"]
        for judge in DEFAULT_JUDGES
        for repeat in range(1, 4)
    ]


def test_prepare_pins_two_real_transcripts():
    manifest = prepare_manifest()
    assert set(manifest["hypotheses"]) == {"H2", "H3"}
    assert manifest["expected_judgments"] == 12
    assert all(len(item["transcript_sha256"]) == 64 for item in manifest["hypotheses"].values())


def test_three_of_three_per_group_passes():
    manifest = prepare_manifest()
    result = analyze(manifest, complete_set(manifest))
    assert result["gate_e1_passed"] is True
    assert all(group["agreement_rate"] == 1.0 for group in result["groups"])


def test_two_of_three_fails_eighty_percent_gate():
    manifest = prepare_manifest()
    items = complete_set(manifest)
    items[0]["verdict"] = "CONFIRMED"
    result = analyze(manifest, items)
    assert result["gate_e1_passed"] is False
    assert result["groups"][0]["agreement_rate"] == pytest.approx(2 / 3, abs=0.0001)


def test_rejects_transcript_drift():
    manifest = prepare_manifest()
    item = judgment(manifest, "H2", DEFAULT_JUDGES[0], 1)
    item["transcript_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="transcription différente"):
        analyze(manifest, [item])


def test_rejects_duplicate_repeat():
    manifest = prepare_manifest()
    item = judgment(manifest, "H2", DEFAULT_JUDGES[0], 1)
    with pytest.raises(ValueError, match="dupliqué"):
        analyze(manifest, [item, deepcopy(item)])
