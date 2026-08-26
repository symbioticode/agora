#!/usr/bin/env python3
"""Evaluate the preregistered LAB-2 campaign without any provider call."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / "labs" / "LAB-2" / "manifest.json"


def load_records(root: Path) -> list[dict]:
    records = []
    for path in sorted(root.glob("*/AGO-EXP-*.json")):
        try:
            records.append(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            continue
    return records


def evaluate(manifest: dict, records: list[dict]) -> dict:
    objective = manifest["objective"]
    cases = {case["hypothesis"]: case for case in manifest["cases"]}
    matched = defaultdict(list)
    for record in records:
        if record.get("objective") == objective and record.get("question") in cases:
            matched[record["question"]].append(record)

    case_results = []
    group_runs = defaultdict(lambda: {"completed": 0, "passed": 0})
    initial = manifest["execution"]["active_target_repetitions_per_case"]
    maximum = manifest["execution"]["maximum_repetitions_per_case"]
    decisive_failure = False

    for case in manifest["cases"]:
        runs = matched[case["hypothesis"]]
        completed = [run for run in runs if run.get("status") == "COMPLETED" and isinstance(run.get("machine_judgment"), dict)]
        passed = []
        for run in completed:
            verdict = run["machine_judgment"].get("verdict")
            confidence = run["machine_judgment"].get("confidence")
            ok = verdict in case["accepted_verdicts"] and isinstance(confidence, (int, float))
            if "minimum_confidence" in case:
                ok = ok and confidence >= case["minimum_confidence"]
            if "maximum_confidence_exclusive" in case:
                ok = ok and confidence < case["maximum_confidence_exclusive"]
            if ok:
                passed.append(run)

        completion_rate = len(completed) / len(runs) if runs else None
        pass_rate = len(passed) / len(completed) if completed else None
        tranche_complete = len(runs) >= initial
        case_pass = bool(
            tranche_complete
            and completion_rate >= manifest["gates"]["minimum_pipeline_completion_rate"]
            and pass_rate >= manifest["gates"]["minimum_case_pass_rate"]
        )
        if tranche_complete and not case_pass:
            decisive_failure = True
        group_runs[case["group"]]["completed"] += len(completed)
        group_runs[case["group"]]["passed"] += len(passed)
        case_results.append({
            "id": case["id"], "group": case["group"], "runs": len(runs),
            "completed": len(completed), "passed": len(passed),
            "completion_rate": completion_rate, "pass_rate": pass_rate,
            "tranche_complete": tranche_complete, "gate": "PASS" if case_pass else "FAIL" if tranche_complete else "PENDING",
            "remaining_initial": max(0, initial - len(runs)),
            "remaining_maximum": max(0, maximum - len(runs)),
        })

    group_results = {}
    for group in {case["group"] for case in manifest["cases"]}:
        values = group_runs[group]
        rate = values["passed"] / values["completed"] if values["completed"] else None
        complete = all(item["tranche_complete"] for item in case_results if item["group"] == group)
        group_results[group] = {
            **values, "pass_rate": rate, "complete": complete,
            "gate": "PASS" if complete and rate >= manifest["gates"]["minimum_group_pass_rate"] else "FAIL" if complete else "PENDING",
        }
        if group_results[group]["gate"] == "FAIL":
            decisive_failure = True

    campaign_complete = all(item["tranche_complete"] for item in case_results)
    status = "FAIL" if decisive_failure else "PASS" if campaign_complete and all(item["gate"] == "PASS" for item in group_results.values()) else "PENDING"
    return {"lab": manifest["id"], "status": status, "campaign_complete": campaign_complete, "matched_runs": sum(len(items) for items in matched.values()), "cases": case_results, "groups": group_results}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiments", type=Path, default=REPO / "experiments")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    result = evaluate(manifest, load_records(args.experiments))
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"LAB-2 {result['status']} — {result['matched_runs']} runs reconnus")
        for item in result["cases"]:
            print(f"  {item['id']}: {item['gate']} — runs={item['runs']} completed={item['completed']} pass={item['passed']} reste={item['remaining_initial']}")
    return 0 if result["status"] == "PASS" else 1 if result["status"] == "FAIL" else 2


if __name__ == "__main__":
    sys.exit(main())
