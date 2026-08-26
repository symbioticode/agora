from scripts.step3_rounds import analyze, prepare_manifest, projected_call_cost


def item(manifest, rounds, classification="NOVEL"):
    return {
        "rounds": rounds,
        "hypothesis_sha256": manifest["hypothesis_sha256"],
        "turn_assessments": [
            {"round": i // 2, "classification": classification}
            for i in range(2 * (rounds + 1))
        ],
        "usage": {"tokens": 100},
    }


def test_manifest_freezes_rounds_and_thresholds():
    manifest = prepare_manifest()
    assert manifest["rounds"] == [2, 3, 4, 5, 6]
    assert manifest["degradation_rule"] == {"max_drift_rate": 0.10, "min_novelty_rate": 0.25}


def test_projected_call_cost_is_positive_and_provider_specific():
    anthropic = projected_call_cost("anthropic", "hypothèse", 900)
    deepseek = projected_call_cost("deepseek", "hypothèse", 900)
    assert anthropic > deepseek > 0


def test_complete_novel_series_recommends_six():
    manifest = prepare_manifest()
    result = analyze(manifest, [item(manifest, rounds) for rounds in manifest["rounds"]])
    assert result["recommended_default_rounds"] == 6


def test_first_drift_recommends_previous_setting():
    manifest = prepare_manifest()
    items = [item(manifest, rounds, "DRIFT" if rounds == 5 else "NOVEL") for rounds in manifest["rounds"]]
    result = analyze(manifest, items)
    assert result["first_degraded_setting"] == 5
    assert result["recommended_default_rounds"] == 4
