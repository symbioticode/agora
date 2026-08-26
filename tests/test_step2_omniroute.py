import json

from scripts.step2_omniroute import DEFAULT_MODELS, judge_user
from scripts.step2_stability import prepare_manifest


def test_long_manifest_has_two_models_and_forty_judgments():
    manifest = prepare_manifest(judges=DEFAULT_MODELS, repeats=10, protocol="test")
    assert manifest["judges"] == list(DEFAULT_MODELS)
    assert manifest["expected_judgments"] == 40
    assert manifest["repeats_per_judge"] == 10


def test_two_models_may_share_provider_but_remain_distinct():
    models = ("mistral/mistral-small-latest", "mistral/magistral-small-latest")
    manifest = prepare_manifest(judges=models, repeats=10, protocol="test")
    assert len(set(manifest["judges"])) == 2
    assert {model.split("/", 1)[0] for model in manifest["judges"]} == {"mistral"}


def test_judge_prompt_contains_hypothesis_and_all_turns():
    transcript = [
        {"round": 0, "agent": "A", "content": "position A"},
        {"round": 0, "agent": "B", "content": "position B"},
    ]
    rendered = judge_user("hypothèse test", transcript)
    assert "hypothèse test" in rendered
    assert "Agent A: position A" in rendered
    assert "Agent B: position B" in rendered
