#!/usr/bin/env python3
"""Extract metrics from all session files."""
import json, glob, os, statistics
from datetime import datetime

sessions = sorted(glob.glob("sessions/*.json"))

# Group by hypothesis
groups = {}
for f in sessions:
    d = json.load(open(f, "r", encoding="utf-8"))
    h = d['hypothesis']
    if h not in groups:
        groups[h] = []
    groups[h].append((f, d))

def analyze_hypothesis(name, runs):
    """Analyze runs for a hypothesis."""
    print(f"\n=== {name} ({len(runs)} runs) ===")
    
    verdicts = []
    confidences = []
    disagreement_count = 0
    convergence_lt2 = 0
    
    for f, d in runs:
        v = d['verdict']
        verdict = v['verdict']
        conf = v['confidence']
        disagreement = v.get('disagreement', [])
        transcript = d.get('transcript', [])
        
        verdicts.append(verdict)
        confidences.append(conf)
        
        has_d = len(disagreement) > 0
        if has_d:
            disagreement_count += 1
        
        # Check convergence < 2 tours: both agents at round 1?
        agent_rounds = {}
        for t in transcript:
            r = t["round"]
            if r not in agent_rounds:
                agent_rounds[r] = set()
            agent_rounds[r].add(t["agent"])
        
        both_at_r1 = "A" in agent_rounds.get(1, set()) and "B" in agent_rounds.get(1, set())
        if not both_at_r1:
            convergence_lt2 += 1
        
        fname = os.path.basename(f)
        print(f"  {fname}: {verdict} ({conf:.2f}) | disagr={len(disagreement)} | both_at_r1={both_at_r1}")
    
    # Stats
    if confidences:
        mean_c = statistics.mean(confidences)
        std_c = statistics.stdev(confidences) if len(confidences) > 1 else 0.0
    else:
        mean_c = std_c = 0.0
    
    verdict_dist = {}
    for v in verdicts:
        verdict_dist[v] = verdict_dist.get(v, 0) + 1
    
    print(f"  Verdicts: {verdict_dist}")
    print(f"  Confidence: mean={mean_c:.3f}, std={std_c:.3f}")
    print(f"  Disagreement rate: {disagreement_count}/{len(runs)} = {disagreement_count/len(runs)*100:.0f}%")
    print(f"  Convergence < 2 tours: {convergence_lt2}/{len(runs)} = {convergence_lt2/len(runs)*100:.0f}%")
    
    return {
        'runs': len(runs),
        'verdicts': verdicts,
        'verdict_dist': verdict_dist,
        'confidence_mean': mean_c,
        'confidence_std': std_c,
        'disagreement_rate': disagreement_count/len(runs) if runs else 0,
        'convergence_lt2_rate': convergence_lt2/len(runs) if runs else 0,
    }

# Analyze each hypothesis
results = {}
for h, runs in groups.items():
    short = h[:60]
    results[h] = analyze_hypothesis(short, runs)

# Summary table
print("\n\n=== SUMMARY TABLE ===")
print("| Hypothesis | Runs | Verdicts | Confidence mean±std | Disagr | Conv<2T |")
print("|------------|------|----------|---------------------|--------|---------|")
for h, r in results.items():
    short = h[:40]
    vd = ','.join(f"{k}:{v}" for k,v in r['verdict_dist'].items())
    print(f"| {short} | {r['runs']} | {vd} | {r['confidence_mean']:.3f}±{r['confidence_std']:.3f} | {r['disagreement_rate']*100:.0f}% | {r['convergence_lt2_rate']*100:.0f}% |")