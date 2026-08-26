from agora.engine import DEFAULT_ROUNDS, DebateEngine


class FakeGateway:
    def anthropic(self, model, system, user, temp):
        if "juge impartial" in system:
            return '{"verdict":"CONFIRMED","confidence":0.9,"agreement":[],"disagreement":[],"reasoning":"ok"}', 0
        return "réponse empiriste", 0

    def deepseek(self, model, system, user, temp):
        if "juge impartial" in system:
            return '{"verdict":"CONFIRMED","confidence":0.9,"agreement":[],"disagreement":[],"reasoning":"ok"}', 0
        return "réponse rationaliste", 0


def test_engine_qualified_path_without_network():
    result = DebateEngine(FakeGateway(), judge_selector=lambda: "deepseek").run("Un fait simple")
    assert result["configuration"] == {"mode": "QUALIFIED", "rounds": DEFAULT_ROUNDS}
    assert result["models"]["A"].startswith("anthropic:")
    assert result["models"]["B"].startswith("deepseek:")
    assert len(result["transcript"]) == (DEFAULT_ROUNDS + 1) * 2
    assert result["verdict"]["verdict"] == "CONFIRMED"
    assert result["verdict"]["rationale"] == "ok"


def test_engine_rejects_unqualified_round_count():
    try:
        DebateEngine(FakeGateway()).run("question", rounds=3)
    except ValueError as exc:
        assert "impose 6 tours" in str(exc)
    else:
        raise AssertionError("non-qualified rounds accepted")
