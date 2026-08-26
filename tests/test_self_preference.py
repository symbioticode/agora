import json

from scripts.self_preference import analyze, prepare_manifest, render_user


def item(manifest, judge, condition, a, b, winner):
    return {"condition": condition, "judge": judge, "transcript_sha256": manifest["transcript_sha256"],
            "score_A": a, "score_B": b, "winner": winner}


def test_labels_change_without_changing_content():
    manifest = prepare_manifest()
    source = json.loads(open(manifest["source_session"], encoding="utf-8").read())
    truthful = render_user(manifest, source["transcript"], "truthful")
    swapped = render_user(manifest, source["transcript"], "swapped")
    assert truthful.replace("Anthropic", "X").replace("DeepSeek", "Y") == swapped.replace("DeepSeek", "X").replace("Anthropic", "Y")


def test_analysis_passes_small_invariant_effect():
    manifest = prepare_manifest()
    rows = []
    for judge in manifest["judges"]:
        rows += [item(manifest, judge, "truthful", 70, 60, "A"),
                 item(manifest, judge, "masked", 69, 61, "A"),
                 item(manifest, judge, "swapped", 68, 62, "A")]
    result = analyze(manifest, rows)
    assert result["complete"] and result["criterion_passed"]


def test_analysis_detects_paid_label_preference():
    manifest = prepare_manifest()
    rows = []
    for judge in manifest["judges"]:
        rows += [item(manifest, judge, "truthful", 70, 60, "A"),
                 item(manifest, judge, "masked", 65, 65, "TIE"),
                 item(manifest, judge, "swapped", 55, 75, "B")]
    assert not analyze(manifest, rows)["criterion_passed"]
