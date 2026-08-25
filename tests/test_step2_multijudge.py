from copy import deepcopy

import pytest

from scripts.step2_multijudge import aggregate_votes, prepare_manifest


def evidence(manifest, hypothesis_id, judge, verdicts):
    return [
        {
            "hypothesis_id": hypothesis_id,
            "judge": judge,
            "repeat": repeat,
            "transcript_sha256": manifest["hypotheses"][hypothesis_id][
                "transcript_sha256"
            ],
            "verdict": verdict,
        }
        for repeat, verdict in enumerate(verdicts, 1)
    ]


def complete_evidence(manifest, verdict="NUANCED"):
    items = []
    for hypothesis_id in manifest["hypotheses"]:
        for judge, metadata in manifest["judges"].items():
            items.extend(
                evidence(
                    manifest,
                    hypothesis_id,
                    judge,
                    [verdict] * metadata["expected_repeats"],
                )
            )
    return items


def test_manifest_equalizes_three_distinct_providers():
    manifest = prepare_manifest()
    assert set(manifest["judges"]) == {
        "anthropic:claude-sonnet-4-5-20250929",
        "deepseek:deepseek-v4-flash",
        "mistral/mistral-small-latest",
    }
    assert {item["provider"] for item in manifest["judges"].values()} == {
        "anthropic",
        "deepseek",
        "mistral",
    }
    assert manifest["provider_weight"] == "one modal vote per provider"


def test_three_provider_majority_passes_fallback():
    manifest = prepare_manifest()
    items = complete_evidence(manifest)
    result = aggregate_votes(manifest, items)
    assert result["complete"] is True
    assert result["retrospective_supports_multijudge"] is True
    assert result["fallback_gate_status"] == "RETROSPECTIVE_NOT_PREREGISTERED"
    assert all(group["collective_verdict"] == "NUANCED" for group in result["groups"])


def test_one_one_one_returns_pending():
    manifest = prepare_manifest()
    items = complete_evidence(manifest)
    target = "H3"
    replacements = {
        "anthropic:claude-sonnet-4-5-20250929": "CONFIRMED",
        "deepseek:deepseek-v4-flash": "NUANCED",
        "mistral/mistral-small-latest": "REJECTED",
    }
    for item in items:
        if item["hypothesis_id"] == target:
            item["verdict"] = replacements[item["judge"]]
    result = aggregate_votes(manifest, items)
    group = next(group for group in result["groups"] if group["hypothesis_id"] == target)
    assert group["collective_verdict"] == "PENDING"
    assert group["majority"] is False
    assert result["retrospective_supports_multijudge"] is False


def test_provider_repetitions_never_create_extra_vote_weight():
    manifest = prepare_manifest()
    items = complete_evidence(manifest, verdict="CONFIRMED")
    for item in items:
        if item["hypothesis_id"] == "H3" and item["judge"].startswith("deepseek:"):
            item["verdict"] = "REJECTED" if item["repeat"] == 1 else "NUANCED"
    result = aggregate_votes(manifest, items)
    group = next(group for group in result["groups"] if group["hypothesis_id"] == "H3")
    assert len(group["provider_votes"]) == 3
    deepseek = next(vote for vote in group["provider_votes"] if vote["provider"] == "deepseek")
    assert deepseek["vote"] == "NUANCED"
    assert deepseek["within_provider_agreement"] == pytest.approx(2 / 3, abs=0.0001)


def test_incomplete_or_duplicate_evidence_is_rejected_conservatively():
    manifest = prepare_manifest()
    items = complete_evidence(manifest)
    result = aggregate_votes(manifest, items[:-1])
    assert result["complete"] is False
    assert result["retrospective_supports_multijudge"] is False
    duplicate = deepcopy(items[0])
    with pytest.raises(ValueError, match="dupliqué"):
        aggregate_votes(manifest, items + [duplicate])


def test_rejects_transcript_or_verdict_drift():
    manifest = prepare_manifest()
    item = complete_evidence(manifest)[0]
    item["transcript_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="transcription différente"):
        aggregate_votes(manifest, [item])
    item["transcript_sha256"] = manifest["hypotheses"]["H2"]["transcript_sha256"]
    item["verdict"] = "MAYBE"
    with pytest.raises(ValueError, match="verdict invalide"):
        aggregate_votes(manifest, [item])
