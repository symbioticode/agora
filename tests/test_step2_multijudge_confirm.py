from copy import deepcopy

import pytest

from scripts.step2_multijudge_confirm import analyze, prepare_manifest


def judgment(manifest, hypothesis_id, judge, verdict):
    return {
        "hypothesis_id": hypothesis_id,
        "judge": judge,
        "transcript_sha256": manifest["hypotheses"][hypothesis_id][
            "transcript_sha256"
        ],
        "verdict": verdict,
        "confidence": 0.75,
    }


def complete_set(manifest, verdict="NUANCED"):
    return [
        judgment(manifest, hypothesis_id, judge, verdict)
        for hypothesis_id in manifest["hypotheses"]
        for judge in manifest["judges"]
    ]


def test_confirmation_manifest_freezes_six_new_votes():
    manifest = prepare_manifest()
    assert manifest["prospective"] is True
    assert manifest["expected_judgments"] == 6
    assert len(manifest["judges"]) == 3
    assert len({item["provider"] for item in manifest["judges"].values()}) == 3
    assert manifest["tie_rule"] == "1-1-1 becomes PENDING"


def test_two_of_three_confirms_each_hypothesis():
    manifest = prepare_manifest()
    items = complete_set(manifest)
    items[0]["verdict"] = "PENDING"
    result = analyze(manifest, items)
    assert result["complete"] is True
    assert result["confirmation_gate_passed"] is True
    assert result["groups"][0]["collective_verdict"] == "NUANCED"


def test_one_one_one_is_pending_and_fails():
    manifest = prepare_manifest()
    items = complete_set(manifest)
    verdicts = iter(("CONFIRMED", "NUANCED", "REJECTED"))
    for item in items:
        if item["hypothesis_id"] == "H3":
            item["verdict"] = next(verdicts)
    result = analyze(manifest, items)
    group = next(group for group in result["groups"] if group["hypothesis_id"] == "H3")
    assert group["collective_verdict"] == "PENDING"
    assert result["confirmation_gate_passed"] is False


def test_incomplete_duplicate_or_tampered_votes_fail_closed():
    manifest = prepare_manifest()
    items = complete_set(manifest)
    assert analyze(manifest, items[:-1])["confirmation_gate_passed"] is False
    with pytest.raises(ValueError, match="dupliqué"):
        analyze(manifest, items + [deepcopy(items[0])])
    tampered = deepcopy(items[0])
    tampered["transcript_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="transcription différente"):
        analyze(manifest, [tampered])
