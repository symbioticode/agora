from scripts.temporal_stability import analyze, prepare_manifest


def build(manifest, outcomes):
    rows = []
    for hypothesis, repeats in outcomes.items():
        for repeat, verdicts in enumerate(repeats, 1):
            for judge, verdict in zip(manifest["judges"], verdicts):
                rows.append({"hypothesis_id": hypothesis, "repeat": repeat, "judge": judge,
                             "transcript_sha256": manifest["hypotheses"][hypothesis]["transcript_sha256"],
                             "verdict": verdict, "confidence": .8})
    return rows


def test_three_collective_cycles_stable():
    manifest = prepare_manifest()
    rows = build(manifest, {"H2": [["CONFIRMED"] * 3] * 3, "H3": [["NUANCED"] * 3] * 3})
    result = analyze(manifest, rows)
    assert result["complete"] and result["criterion_passed"]


def test_collective_change_is_not_stable():
    manifest = prepare_manifest()
    rows = build(manifest, {"H2": [["CONFIRMED"] * 3] * 3,
                            "H3": [["NUANCED"] * 3, ["PENDING"] * 3, ["NUANCED"] * 3]})
    assert not analyze(manifest, rows)["criterion_passed"]
