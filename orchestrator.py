#!/usr/bin/env python3
"""
orchestrator.py — Agora / Orchestrateur principal (~90 lignes)
Usage: python orchestrator.py --hypothesis "..." --rounds 3
"""
import os, json, re, argparse, sys, hashlib, time
from datetime import datetime
from pathlib import Path

from anthropic import Anthropic
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
REPO = Path(__file__).parent
SESSIONS = REPO / "sessions"
SESSIONS.mkdir(exist_ok=True)

ANTHROPIC = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
DEEPSEEK = OpenAI(base_url="https://api.deepseek.com/v1", api_key=os.getenv("DEEPSEEK_API_KEY"))

MODEL_A = "claude-sonnet-4-5"
MODEL_B = "deepseek-v4-flash"
DEFAULT_ROUNDS = 3
TEMP_DEBATE = 0.7
TEMP_JUDGE = 0.0


def pick_judge():
    """Alterne juge entre Anthropic et DeepSeek (pas de provider tiers requis)."""
    seed = str(int(time.time() * 1000))
    h = hashlib.md5(seed.encode()).hexdigest()
    return "anthropic" if int(h, 16) % 2 == 0 else "deepseek"


MINDSETS = {
    "A": (REPO / "mindsets" / "empiricist.md").read_text(),
    "B": (REPO / "mindsets" / "rationalist.md").read_text(),
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


def call_anthropic(model, system, user, temp):
    r = ANTHROPIC.messages.create(model=model, max_tokens=2000, temperature=temp,
                                   system=system, messages=[{"role": "user", "content": user}])
    return r.content[0].text


def call_deepseek(model, system, user, temp):
    r = DEEPSEEK.chat.completions.create(model=model, max_tokens=2000, temperature=temp,
                                          messages=[{"role": "system", "content": system},
                                                    {"role": "user", "content": user}])
    return r.choices[0].message.content


def agent_turn(agent_id, hypothesis, history, round_num):
    system = MINDSETS[agent_id]
    if round_num == 0:
        user = f"Hypothèse: {hypothesis}\n\nDonne ta position initiale. Sois concis."
    else:
        other = "B" if agent_id == "A" else "A"
        last_other = history[-1][other]
        user = (f"Hypothèse (ré-ancrée): {hypothesis}\n\n"
                f"Tour {round_num}. L'adversaire ({other}) a répondu:\n{last_other}\n\n"
                f"Maintiens, révises ou nuances ta position. Cite explicitement ce qui te fait changer d'avis.")
    if agent_id == "A":
        return call_anthropic(MODEL_A, system, user, TEMP_DEBATE)
    else:
        return call_deepseek(MODEL_B, system, user, TEMP_DEBATE)


def extract_json(text: str) -> dict:
    """Extrait le premier objet JSON valide d'une chaîne."""
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        try:
            return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise ValueError(f"Impossible d'extraire JSON valide: {text[:200]}...")


def judge_verdict(hypothesis, transcript):
    transcript_str = "\n".join(
        f"Tour {t['round']} - Agent {t['agent']}: {t['content']}" for t in transcript
    )
    user = f"Hypothèse: {hypothesis}\n\nDébat:\n{transcript_str}"

    judge_provider = pick_judge()
    if judge_provider == "anthropic":
        model = MODEL_A
        raw = call_anthropic(model, JUDGE_PROMPT, user, TEMP_JUDGE)
    else:
        model = MODEL_B
        raw = call_deepseek(model, JUDGE_PROMPT, user, TEMP_JUDGE)
    return extract_json(raw), f"{judge_provider}:{model}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hypothesis", required=True)
    parser.add_argument("--rounds", type=int, default=DEFAULT_ROUNDS)
    args = parser.parse_args()

    history = []
    transcript = []

    for r in range(args.rounds + 1):
        for agent in ("A", "B"):
            resp = agent_turn(agent, args.hypothesis, history, r)
            if r == 0:
                history.append({"A": resp if agent == "A" else "", "B": resp if agent == "B" else ""})
            else:
                history[-1][agent] = resp
            transcript.append({"round": r, "agent": agent, "content": resp})

    verdict, judge_model = judge_verdict(args.hypothesis, transcript)

    session = {
        "hypothesis": args.hypothesis,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "models": {"A": MODEL_A, "B": MODEL_B, "judge": judge_model},
        "transcript": transcript,
        "verdict": verdict,
    }

    fname = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    (SESSIONS / fname).write_text(json.dumps(session, indent=2, ensure_ascii=False))

    print(json.dumps(verdict, indent=2, ensure_ascii=False))
    print(f"\nSession saved: sessions/{fname}")


if __name__ == "__main__":
    main()