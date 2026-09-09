from types import SimpleNamespace

from agora.engine import DEEPSEEK_TOKEN_BUDGET, DEFAULT_ROUNDS, JUDGE_PROMPT, MAX_AGENT_CHARACTERS, MAX_AGENT_WORDS, DebateEngine


class FakeGateway:
    def __init__(self):
        self.agent_prompts = []

    def ready(self, providers=("anthropic", "deepseek")):
        return True

    def anthropic(self, model, system, user, temp):
        if "juge impartial" in system:
            return '{"verdict":"CONFIRMED","confidence":0.9,"agreement":[],"disagreement":[],"reasoning":"ok"}', 0
        self.agent_prompts.append(user)
        return "réponse empiriste", 0

    def deepseek(self, model, system, user, temp):
        if "juge impartial" in system:
            return '{"verdict":"CONFIRMED","confidence":0.9,"agreement":[],"disagreement":[],"reasoning":"ok"}', 0
        self.agent_prompts.append(user)
        return "réponse rationaliste", 0

    def nvidia(self, model, system, user, temp):
        self.agent_prompts.append(user)
        return "réponse empiriste NVIDIA", 0


def test_engine_qualified_path_without_network():
    events = []
    gateway = FakeGateway()
    result = DebateEngine(gateway, judge_selector=lambda: "deepseek").run("Un fait simple", on_event=events.append)
    assert result["configuration"] == {
        "mode": "QUALIFIED",
        "rounds": DEFAULT_ROUNDS,
        "agent_response_limits": {
            "max_words": MAX_AGENT_WORDS,
            "max_characters": MAX_AGENT_CHARACTERS,
        },
        "provider_token_budgets": {
            "anthropic": 2000,
            "deepseek": DEEPSEEK_TOKEN_BUDGET,
        },
    }
    assert result["models"]["A"].startswith("anthropic:")
    assert result["models"]["B"].startswith("deepseek:")
    assert len(result["transcript"]) == (DEFAULT_ROUNDS + 1) * 2
    assert result["verdict"]["verdict"] == "CONFIRMED"
    assert result["verdict"]["rationale"] == "ok"
    assert len([event for event in events if event["type"] == "turn"]) == (DEFAULT_ROUNDS + 1) * 2
    assert events[-1]["type"] == "judge"
    assert len(gateway.agent_prompts) == (DEFAULT_ROUNDS + 1) * 2
    assert all(f"maximum {MAX_AGENT_WORDS} mots ET {MAX_AGENT_CHARACTERS} caractères" in prompt for prompt in gateway.agent_prompts)
    assert all("réponse inachevée" in prompt for prompt in gateway.agent_prompts)


def test_engine_rejects_unqualified_round_count():
    try:
        DebateEngine(FakeGateway()).run("question", rounds=3)
    except ValueError as exc:
        assert "impose 6 tours" in str(exc)
    else:
        raise AssertionError("non-qualified rounds accepted")


def test_engine_routes_agent_a_to_nvidia_without_anthropic():
    gateway = FakeGateway()
    result = DebateEngine(
        gateway,
        judge_selector=lambda: "deepseek",
        agent_a_provider="nvidia",
    ).run("question")
    assert result["models"]["A"] == "nvidia:meta/llama-3.2-11b-vision-instruct"
    assert result["models"]["B"].startswith("deepseek:")
    assert result["configuration"]["provider_token_budgets"] == {
        "nvidia": 4096,
        "deepseek": DEEPSEEK_TOKEN_BUDGET,
    }


def test_context_is_reanchored_at_every_round():
    gateway = FakeGateway()
    DebateEngine(gateway).run("question", context="SOURCE EXACTE")
    assert len(gateway.agent_prompts) == (DEFAULT_ROUNDS + 1) * 2
    assert all("SOURCE EXACTE" in prompt for prompt in gateway.agent_prompts)


def test_judge_contract_bounds_json_output():
    assert "uniquement avec l'objet JSON" in JUDGE_PROMPT
    assert "au maximum 3 éléments" in JUDGE_PROMPT
    assert "au maximum 600 caractères" in JUDGE_PROMPT


def test_gateway_status_can_be_restored_from_failed_experiment(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "configured")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "configured")
    from agora.engine import ProviderGateway
    gateway = ProviderGateway()
    gateway.restore_from_experiment({
        "observation": {"transcript": [{"agent": "A", "content": "ok"}, {"agent": "B", "content": "partiel"}]},
        "failure": {"message": "Réponse DeepSeek vide"},
    })
    assert gateway.status()["anthropic"]["status"] == "ON"
    assert gateway.status()["deepseek"]["status"] == "DEGRADED"
    assert not gateway.ready()


def test_sonnet5_request_omits_deprecated_temperature(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "configured")
    from agora.engine import ProviderGateway

    captured = {}

    class Messages:
        @staticmethod
        def create(**kwargs):
            captured.update(kwargs)
            return SimpleNamespace(
                stop_reason="end_turn",
                content=[SimpleNamespace(thinking="internal"), SimpleNamespace(text="OK")],
            )

    gateway = ProviderGateway()
    gateway._anthropic = SimpleNamespace(messages=Messages())
    text, retries = gateway.anthropic(
        "claude-sonnet-5", "system", "user", 0.7, max_tokens=64
    )

    assert text == "OK"
    assert retries == 0
    assert captured["model"] == "claude-sonnet-5"
    assert "temperature" not in captured
    assert captured["thinking"] == {"type": "disabled"}
    assert captured["output_config"] == {"effort": "low"}


def test_nvidia_uses_openai_compatible_transport(monkeypatch):
    monkeypatch.setenv("NVIDIA_API_KEY", "configured")
    from agora.engine import ProviderGateway

    captured = {}

    class Completions:
        @staticmethod
        def create(**kwargs):
            captured.update(kwargs)
            choice = SimpleNamespace(
                finish_reason="stop",
                message=SimpleNamespace(content="OK"),
            )
            return SimpleNamespace(choices=[choice])

    gateway = ProviderGateway()
    gateway._nvidia = SimpleNamespace(
        chat=SimpleNamespace(completions=Completions()),
    )
    text, retries = gateway.nvidia(
        "meta/llama-3.2-11b-vision-instruct",
        "system",
        "user",
        0.7,
        max_tokens=64,
    )

    assert text == "OK"
    assert retries == 0
    assert captured["model"] == "meta/llama-3.2-11b-vision-instruct"
    assert captured["temperature"] == 0.7
    assert gateway.status()["nvidia"]["status"] == "ON"


def test_readiness_can_target_nvidia_and_deepseek(monkeypatch):
    monkeypatch.setenv("NVIDIA_API_KEY", "configured")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "configured")
    from agora.engine import ProviderGateway

    gateway = ProviderGateway()
    gateway._state["nvidia"]["status"] = "ON"
    gateway._state["deepseek"]["status"] = "ON"

    assert gateway.ready(("nvidia", "deepseek"))
    assert not gateway.ready(("anthropic", "deepseek"))
