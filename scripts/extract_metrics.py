#!/usr/bin/env python3
"""Extract metrics from H1 session files."""
import json, glob, os, statistics

H1_FILES = sorted(glob.glob(r"sessions/20260716_19*.json"))

print("=== H1 — Disagreement analysis ===")
disagreement_count = 0
convergence_rounds = []

for f in H1_FILES:
    d = json.load(open(f, "r", encoding="utf-8"))
    v = d["verdict"]
    transcript = d.get("transcript", [])
    disagreement = v.get("disagreement", [])
    rounds = sorted(set(t["round"] for t in transcript))
    has_d = len(disagreement) > 0
    if has_d:
        disagreement_count += 1

    # Check convergence: when did both agents have content in the same round?
    # Round 0 is parallel (no cross-reading), so convergence happens at round 1+
    agent_rounds = {}
    for t in transcript:
        r = t["round"]
        if r not in agent_rounds:
            agent_rounds[r] = []
        agent_rounds[r].append(t["agent"])

    # Both agents present = both have spoken
    both_at = [r for r in sorted(agent_rounds.keys()) if len(agent_rounds[r]) == 2]

    fname = os.path.basename(f)
    print(f"  {fname}: verdict={v['verdict']} conf={v['confidence']}")
    print(f"    disagreement[]: {len(disagreement)} items, has_disagreement={has_d}")
    print(f"    rounds present: {rounds}")
    print(f"    both agents at rounds: {both_at}")
    print()

print(f"H1 taux désaccord persistant: {disagreement_count}/{len(H1_FILES)} = {disagreement_count/len(H1_FILES)*100:.0f}%")
print()

# For convergence < 2 tours check:
# We need to see if the debate effectively converged (both agents aligned) by round 1
# This means: after round 0 (parallel), did both agents agree by round 1?
# Check if transcript has content at round 1 for both agents
print("=== Convergence analysis ===")
for f in H1_FILES:
    d = json.load(open(f, "r", encoding="utf-8"))
    transcript = d.get("transcript", [])
    fname = os.path.basename(f)

    # Count rounds with content from both agents
    agent_rounds = {}
    for t in transcript:
        r = t["round"]
        if r not in agent_rounds:
            agent_rounds[r] = set()
        agent_rounds[r].add(t["agent"])

    max_round = max(agent_rounds.keys()) if agent_rounds else 0
    both_at_round_1 = "A" in agent_rounds.get(1, set()) and "B" in agent_rounds.get(1, set())

    print(f"  {fname}: max_round={max_round}, both_agents_at_r1={both_at_round_1}")
