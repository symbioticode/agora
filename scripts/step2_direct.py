#!/usr/bin/env python3
"""Gate E1 direct Anthropic↔DeepSeek avec fenêtre et budgets durs."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, time as wall_time, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

try:
    from scripts.step2_stability import REPO, analyze, digest, prepare_manifest
    from scripts.step2_omniroute import judge_user, load_sources
except ModuleNotFoundError:
    from step2_stability import REPO, analyze, digest, prepare_manifest
    from step2_omniroute import judge_user, load_sources

if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from orchestrator import JUDGE_PROMPT, extract_json

load_dotenv(REPO / ".env")

JUDGES = ("anthropic:claude-sonnet-4-5-20250929", "deepseek:deepseek-v4-flash")
RATES = {
    # USD / million tokens. Conservateurs et surchargeables par CLI.
    "anthropic": {"input": 3.0, "output": 15.0},
    "deepseek": {"input": 1.0, "output": 5.0},
}


def in_window(now: datetime, start: wall_time = wall_time(0), end: wall_time = wall_time(4)) -> bool:
    local = now.astimezone(ZoneInfo("America/Toronto")).time().replace(tzinfo=None)
    return start <= local < end


def estimated_cost(provider: str, tokens_in: int, tokens_out: int, rates=RATES) -> float:
    return (tokens_in * rates[provider]["input"] + tokens_out * rates[provider]["output"]) / 1_000_000


def usage_cost(provider: str, usage: dict) -> float:
    """Estimation conservatrice, cache inclus (Anthropic write 1.25x/read 0.1x)."""
    if provider == "anthropic":
        weighted_in = (
            usage.get("input_tokens", 0)
            + 1.25 * usage.get("cache_creation_input_tokens", 0)
            + 0.10 * usage.get("cache_read_input_tokens", 0)
        )
    else:
        # DeepSeek est beaucoup moins cher; conserver le tarif plafond 1 USD/MTok.
        weighted_in = usage.get("prompt_cache_miss_tokens", usage.get("input_tokens", 0))
        weighted_in += 0.02 * usage.get("prompt_cache_hit_tokens", 0)
    return estimated_cost(provider, int(weighted_in), usage.get("output_tokens", 0))


def call_direct(judge: str, user: str, max_tokens: int) -> tuple[str, dict, float]:
    started = time.monotonic()
    if judge.startswith("anthropic:"):
        from anthropic import Anthropic
        model = judge.split(":", 1)[1]
        response = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"]).messages.create(
            model=model, max_tokens=max_tokens, temperature=0,
            system=JUDGE_PROMPT, messages=[{"role": "user", "content": user}],
            cache_control={"type": "ephemeral"},
        )
        raw = response.content[0].text
        usage = {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "cache_creation_input_tokens": getattr(response.usage, "cache_creation_input_tokens", 0) or 0,
            "cache_read_input_tokens": getattr(response.usage, "cache_read_input_tokens", 0) or 0,
        }
    else:
        from openai import OpenAI
        model = judge.split(":", 1)[1]
        response = OpenAI(base_url="https://api.deepseek.com/v1", api_key=os.environ["DEEPSEEK_API_KEY"]).chat.completions.create(
            model=model, max_tokens=max_tokens, temperature=0,
            messages=[{"role": "system", "content": JUDGE_PROMPT}, {"role": "user", "content": user}],
            extra_body={"thinking": {"type": "disabled"}},
        )
        raw = response.choices[0].message.content
        raw_usage = response.usage.model_dump()
        usage = {
            "input_tokens": response.usage.prompt_tokens,
            "output_tokens": response.usage.completion_tokens,
            "prompt_cache_hit_tokens": raw_usage.get("prompt_cache_hit_tokens", 0) or 0,
            "prompt_cache_miss_tokens": raw_usage.get("prompt_cache_miss_tokens", response.usage.prompt_tokens) or 0,
        }
    return raw, usage, round(time.monotonic() - started, 3)


def run(output: Path, repeats: int, interval: float, caps: dict[str, float], max_tokens: int) -> int:
    now = datetime.now(timezone.utc)
    if not in_window(now):
        raise RuntimeError("appels directs refusés hors fenêtre 00:00–04:00 America/Toronto")
    for name in ("ANTHROPIC_API_KEY", "DEEPSEEK_API_KEY"):
        if not os.getenv(name):
            raise RuntimeError(f"{name} absent")

    manifest = prepare_manifest(judges=JUDGES, repeats=repeats, protocol="AGORA-E1-step2-direct-v1")
    manifest["offline_only"] = False
    manifest["authorized_window"] = "00:00–04:00 America/Toronto, 2026-08-10"
    manifest["provider_caps_usd"] = caps
    manifest["pricing_assumptions_usd_per_mtoken"] = RATES
    output.mkdir(parents=True, exist_ok=True)
    failures = output.parent / "failures"
    failures.mkdir(parents=True, exist_ok=True)
    manifest_text = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    (output.parent / "manifest.json").write_text(manifest_text, encoding="utf-8")
    sources = load_sources(manifest)
    spend = {"anthropic": 0.0, "deepseek": 0.0}
    for failure in failures.glob("*.json"):
        old = json.loads(failure.read_text(encoding="utf-8"))
        spend[old["provider"]] += float(old.get("estimated_cost_usd", 0))
    completed = 0

    for repeat in range(1, repeats + 1):
        for hypothesis_id, session in sources.items():
            user = judge_user(session["hypothesis"], session["transcript"])
            for judge in JUDGES:
                if not in_window(datetime.now(timezone.utc)):
                    raise RuntimeError("fenêtre 04:00 atteinte; arrêt avant nouvel appel")
                provider = judge.split(":", 1)[0]
                worst_case = estimated_cost(provider, len(user) // 3 + 1000, max_tokens)
                if spend[provider] + worst_case > caps[provider]:
                    raise RuntimeError(f"budget {provider} refusé avant appel: projection {spend[provider] + worst_case:.4f} > {caps[provider]:.4f}")
                slug = re.sub(r"[^a-z0-9]+", "-", judge.lower()).strip("-")
                target = output / f"{hypothesis_id.lower()}-{slug}-{repeat:02d}.json"
                if target.exists():
                    old = json.loads(target.read_text(encoding="utf-8"))
                    spend[provider] += float(old.get("estimated_cost_usd", 0))
                    completed += 1
                    continue
                raw, usage, latency = call_direct(judge, user, max_tokens)
                cost = usage_cost(provider, usage)
                spend[provider] += cost
                try:
                    verdict = extract_json(raw)
                except ValueError as error:
                    failure = {
                        "hypothesis_id": hypothesis_id, "judge": judge, "provider": provider,
                        "repeat": repeat, "usage": usage, "estimated_cost_usd": round(cost, 8),
                        "latency_s": latency, "collected_at": datetime.now(timezone.utc).isoformat(),
                        "error": str(error), "raw_response": raw,
                    }
                    failure_name = f"{hypothesis_id.lower()}-{slug}-{repeat:02d}-{int(time.time())}.json"
                    failure_text = json.dumps(failure, ensure_ascii=False, indent=2) + "\n"
                    (failures / failure_name).write_text(failure_text, encoding="utf-8")
                    raise
                item = {
                    "hypothesis_id": hypothesis_id, "judge": judge, "repeat": repeat,
                    "transcript_sha256": manifest["hypotheses"][hypothesis_id]["transcript_sha256"],
                    "verdict": verdict["verdict"], "confidence": verdict["confidence"],
                    "agreement": verdict.get("agreement", []), "disagreement": verdict.get("disagreement", []),
                    "reasoning": verdict.get("reasoning", ""), "usage": usage,
                    "estimated_cost_usd": round(cost, 8), "latency_s": latency,
                    "collected_at": datetime.now(timezone.utc).isoformat(), "raw_response": raw,
                }
                target.write_text(json.dumps(item, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                completed += 1
                print(f"[{completed}/{manifest['expected_judgments']}] {hypothesis_id} {judge} r{repeat}: {item['verdict']} {item['confidence']} ${cost:.5f}", flush=True)
                if interval:
                    time.sleep(interval)

    judgments = [json.loads(path.read_text(encoding="utf-8")) for path in sorted(output.glob("*.json"))]
    analysis = analyze(manifest, judgments)
    analysis["usage"] = {
        "estimated_spend_usd": {key: round(value, 8) for key, value in spend.items()},
        "caps_usd": caps,
        "within_caps": all(spend[key] <= caps[key] for key in spend),
    }
    analysis_text = json.dumps(analysis, ensure_ascii=False, indent=2) + "\n"
    (output.parent / "analysis.json").write_text(analysis_text, encoding="utf-8")
    return 0 if analysis["gate_e1_passed"] else 2


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=REPO / "results/step2_direct/judgments")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--interval", type=float, default=10)
    parser.add_argument("--max-tokens", type=int, default=1400)
    parser.add_argument("--anthropic-cap", type=float, default=1.50)
    parser.add_argument("--deepseek-cap", type=float, default=1.50)
    args = parser.parse_args()
    if args.repeats < 3:
        parser.error("au moins trois répétitions")
    return run(args.output, args.repeats, args.interval, {"anthropic": args.anthropic_cap, "deepseek": args.deepseek_cap}, args.max_tokens)


if __name__ == "__main__":
    raise SystemExit(main())
