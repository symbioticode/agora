"""Shared AGORA debate engine used by CLI and web adapters."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Callable

from anthropic import Anthropic
from openai import OpenAI

REPO = Path(__file__).resolve().parent.parent
MODEL_A = "claude-sonnet-4-5"
MODEL_B = "deepseek-v4-flash"
DEFAULT_ROUNDS = 6
TEMP_DEBATE = 0.7
TEMP_JUDGE = 0.0

MINDSETS = {
    "A": (REPO / "mindsets" / "empiricist.md").read_text(encoding="utf-8"),
    "B": (REPO / "mindsets" / "rationalist.md").read_text(encoding="utf-8"),
}

JUDGE_PROMPT = """Tu es un juge impartial à temperature=0.
Tu reçois une hypothèse et un débat entre deux agents aux épistémologies opposées.
Produis un verdict JSON strict avec ces champs exacts:
{
  "verdict": "CONFIRMED" | "NUANCED" | "REJECTED" | "PENDING",
  "confidence": 0.50-1.00,
  "agreement": ["point d'accord 1", "..."],
  "disagreement": ["désaccord persistant 1", "..."],
  "reasoning": "justification concise du verdict"
}
Règles:
- CONFIRMED: hypothèse solidement établie, désaccords mineurs
- NUANCED: vérité partielle, nuances importantes, désaccords persistants
- REJECTED: hypothèse réfutée ou incohérente
- PENDING: irresolvable avec les arguments présents
- confidence ≥ 0.50, ≤ 1.00
- agreement/disagreement: listes de strings, peuvent être vides
"""


def extract_json(text: str) -> dict:
    """Extract the first valid JSON object from a provider response."""
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        try:
            return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Impossible d'extraire JSON valide: {text[:200]}...") from exc


class ProviderGateway:
    """Lazy provider clients: importing AGORA never requires API credentials."""

    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self._anthropic = None
        self._deepseek = None

    def _retry(self, call: Callable[[], str]) -> tuple[str, int]:
        for attempt in range(self.max_retries):
            try:
                return call(), attempt
            except Exception:
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(2**attempt)
        raise RuntimeError("retry loop exhausted")

    def anthropic(self, model: str, system: str, user: str, temp: float) -> tuple[str, int]:
        if self._anthropic is None:
            key = os.getenv("ANTHROPIC_API_KEY")
            if not key:
                raise RuntimeError("ANTHROPIC_API_KEY absent")
            self._anthropic = Anthropic(api_key=key)

        def invoke() -> str:
            result = self._anthropic.messages.create(
                model=model,
                max_tokens=2000,
                temperature=temp,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            text = result.content[0].text if result.content else ""
            if not text or not text.strip():
                raise RuntimeError("Réponse Anthropic vide")
            return text

        return self._retry(invoke)

    def deepseek(self, model: str, system: str, user: str, temp: float) -> tuple[str, int]:
        if self._deepseek is None:
            key = os.getenv("DEEPSEEK_API_KEY")
            if not key:
                raise RuntimeError("DEEPSEEK_API_KEY absent")
            self._deepseek = OpenAI(base_url="https://api.deepseek.com/v1", api_key=key)

        def invoke() -> str:
            result = self._deepseek.chat.completions.create(
                model=model,
                max_tokens=2000,
                temperature=temp,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
            text = result.choices[0].message.content if result.choices else ""
            if not text or not text.strip():
                raise RuntimeError("Réponse DeepSeek vide")
            return text

        return self._retry(invoke)


class DebateEngine:
    """Qualified two-provider debate configuration."""

    def __init__(self, gateway=None, judge_selector: Callable[[], str] | None = None):
        self.gateway = gateway or ProviderGateway()
        self.judge_selector = judge_selector or (lambda: "deepseek")

    def _agent_turn(self, agent: str, hypothesis: str, context: str, history: list, round_num: int):
        if round_num == 0:
            user = f"Hypothèse: {hypothesis}"
            if context:
                user += f"\n\nContexte déclaré:\n{context}"
            user += "\n\nDonne ta position initiale. Sois concis."
        else:
            other = "B" if agent == "A" else "A"
            user = (
                f"Hypothèse (ré-ancrée): {hypothesis}\n\n"
                f"Tour {round_num}. L'adversaire ({other}) a répondu:\n{history[-1][other]}\n\n"
                "Maintiens, révises ou nuances ta position. "
                "Cite explicitement ce qui te fait changer d'avis."
            )
        if agent == "A":
            return self.gateway.anthropic(MODEL_A, MINDSETS[agent], user, TEMP_DEBATE)
        return self.gateway.deepseek(MODEL_B, MINDSETS[agent], user, TEMP_DEBATE)

    def _judge(self, hypothesis: str, transcript: list[dict]):
        transcript_text = "\n".join(
            f"Tour {turn['round']} - Agent {turn['agent']}: {turn['content']}"
            for turn in transcript
        )
        user = f"Hypothèse: {hypothesis}\n\nDébat:\n{transcript_text}"
        provider = self.judge_selector()
        if provider == "anthropic":
            raw, retries = self.gateway.anthropic(MODEL_A, JUDGE_PROMPT, user, TEMP_JUDGE)
            model = f"anthropic:{MODEL_A}"
        elif provider == "deepseek":
            raw, retries = self.gateway.deepseek(MODEL_B, JUDGE_PROMPT, user, TEMP_JUDGE)
            model = f"deepseek:{MODEL_B}"
        else:
            raise ValueError(f"Juge non supporté: {provider}")
        verdict = extract_json(raw)
        if "rationale" not in verdict and "reasoning" in verdict:
            verdict["rationale"] = verdict["reasoning"]
        return verdict, model, retries

    def run(self, hypothesis: str, context: str = "", rounds: int = DEFAULT_ROUNDS, on_event=None) -> dict:
        hypothesis = hypothesis.strip()
        context = context.strip()
        if not hypothesis:
            raise ValueError("L'hypothèse est obligatoire")
        if len(hypothesis) > 4000:
            raise ValueError("L'hypothèse dépasse 4000 caractères")
        if len(context) > 20_000:
            raise ValueError("Le contexte dépasse 20000 caractères")
        if rounds != DEFAULT_ROUNDS:
            raise ValueError(f"Le mode qualifié impose {DEFAULT_ROUNDS} tours")

        started = time.monotonic()
        history: list[dict] = []
        transcript: list[dict] = []
        retries = {"A": 0, "B": 0, "judge": 0}
        for round_num in range(rounds + 1):
            for agent in ("A", "B"):
                response, attempts = self._agent_turn(agent, hypothesis, context, history, round_num)
                retries[agent] += attempts
                if round_num == 0:
                    history.append({"A": response if agent == "A" else "", "B": response if agent == "B" else ""})
                else:
                    history[-1][agent] = response
                transcript.append({"round": round_num, "agent": agent, "content": response})
                if on_event:
                    on_event({"type": "turn", "turn": transcript[-1].copy()})

        if on_event:
            on_event({"type": "judge", "status": "RUNNING"})
        verdict, judge_model, judge_retries = self._judge(hypothesis, transcript)
        retries["judge"] = judge_retries
        return {
            "hypothesis": hypothesis,
            "context": context,
            "configuration": {"mode": "QUALIFIED", "rounds": rounds},
            "models": {"A": f"anthropic:{MODEL_A}", "B": f"deepseek:{MODEL_B}", "judge": judge_model},
            "mindsets": {"A": "empiricist", "B": "rationalist"},
            "retries": retries,
            "duration_seconds": round(time.monotonic() - started, 3),
            "transcript": transcript,
            "verdict": verdict,
        }
