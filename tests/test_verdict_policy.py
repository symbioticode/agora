import pytest

from scripts.verdict_policy import evaluate_action


def test_pending_always_blocks_attached_action():
    assert evaluate_action("PENDING", action_attached=True)["allowed"] is False
    assert (
        evaluate_action("PENDING", action_attached=True, human_approved=True)["allowed"]
        is False
    )


def test_nuanced_is_acceptable_for_ideas_without_action():
    result = evaluate_action("NUANCED", action_attached=False)
    assert result["allowed"] is True
    assert result["mode"] == "IDEA_ONLY"


def test_nuanced_action_requires_human_approval():
    assert evaluate_action("NUANCED", action_attached=True)["allowed"] is False
    assert (
        evaluate_action("NUANCED", action_attached=True, human_approved=True)["allowed"]
        is True
    )


def test_confirmed_action_is_only_a_candidate():
    result = evaluate_action("CONFIRMED", action_attached=True)
    assert result == {
        "allowed": True,
        "mode": "ACTION_CANDIDATE",
        "reason": "confiance suffisante; permissions et postconditions restent requises",
    }


def test_rejected_or_unknown_verdict_cannot_authorize_action():
    assert evaluate_action("REJECTED", action_attached=True)["allowed"] is False
    with pytest.raises(ValueError, match="verdict invalide"):
        evaluate_action("MAYBE", action_attached=True)
