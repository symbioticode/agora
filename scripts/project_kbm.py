#!/usr/bin/env python3
"""Generate the deterministic AGORA projection consumed by KBM 2.0."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from agora.registry import ExperimentRegistry, record_sha256

REPO = Path(__file__).resolve().parent.parent


def atomic_text(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def project(source: Path, destination: Path, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    registry = ExperimentRegistry(source)
    destination.mkdir(parents=True, exist_ok=True)
    existing = {path.stem: path for path in destination.glob("AGO-EXP-*.md")}
    entries = []
    expected = set()

    for record in registry.list():
        experiment_id = record.get("id", "")
        expected.add(experiment_id)
        if record.get("status") != "COMPLETED":
            entries.append({"id": experiment_id, "status": "REFUSED", "reason": "NOT_COMPLETED"})
            continue
        if record.get("record_sha256") != record_sha256(record):
            entries.append({"id": experiment_id, "status": "REFUSED", "reason": "HASH_MISMATCH"})
            continue
        target = destination / f"{experiment_id}.md"
        content = registry.markdown(record) + "\n"
        status = "UNCHANGED" if target.exists() and target.read_text(encoding="utf-8") == content else ("UPDATED" if target.exists() else "NEW")
        if status != "UNCHANGED":
            atomic_text(target, content)
        entries.append({"id": experiment_id, "status": status, "source_sha256": record["record_sha256"], "path": target.name})

    # Files without a canonical source are reported, never deleted.
    for experiment_id, path in sorted(existing.items()):
        if experiment_id not in expected:
            entries.append({"id": experiment_id, "status": "ORPHAN_PRESERVED", "path": path.name})

    manifest = {
        "schema_version": "1.0",
        "generated_at": now.isoformat(),
        "source": "symbioticode/agora",
        "destination": "home-kbm/Projets/AGORA/Experiences",
        "status": "SUCCESS" if not any(item["status"] == "REFUSED" for item in entries) else "PARTIAL",
        "entries": entries,
    }
    atomic_text(destination / "manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=REPO / "experiments")
    parser.add_argument("--destination", type=Path, default=REPO / "projections" / "kbm")
    args = parser.parse_args()
    manifest = project(args.source, args.destination)
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    raise SystemExit(0 if manifest["status"] == "SUCCESS" else 2)


if __name__ == "__main__":
    main()
