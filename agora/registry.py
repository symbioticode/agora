"""Atomic, append-oriented supervised experiment registry."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = "1.0"


def canonical_json(data: dict) -> bytes:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def record_sha256(data: dict) -> str:
    material = {key: value for key, value in data.items() if key != "record_sha256"}
    return hashlib.sha256(canonical_json(material)).hexdigest()


class ExperimentRegistry:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _paths(self):
        return sorted(self.root.glob("*/AGO-EXP-*.json"))

    def reserve_id(self, now: datetime | None = None) -> str:
        now = now or datetime.now(timezone.utc)
        year = now.year
        lock_path = self.root / ".sequence.lock"
        sequence_path = self.root / ".sequence.json"
        import fcntl

        with lock_path.open("a+", encoding="utf-8") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            state = {"year": year, "last": 0}
            if sequence_path.exists():
                state = json.loads(sequence_path.read_text(encoding="utf-8"))
            last = state.get("last", 0) if state.get("year") == year else 0
            last += 1
            self._atomic_write(sequence_path, {"year": year, "last": last})
            return f"AGO-EXP-{year}-{last:04d}"

    @staticmethod
    def _atomic_write(path: Path, data: dict):
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(data, handle, indent=2, ensure_ascii=False)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)

    @staticmethod
    def _git_revision(repo: Path) -> str:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True, check=False
        )
        return result.stdout.strip() if result.returncode == 0 else "UNKNOWN"

    def create(self, debate: dict, metadata: dict | None = None, now: datetime | None = None, experiment_id: str | None = None) -> dict:
        now = now or datetime.now(timezone.utc)
        metadata = metadata or {}
        experiment_id = experiment_id or self.reserve_id(now)
        record = {
            "schema_version": SCHEMA_VERSION,
            "id": experiment_id,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "status": "COMPLETED",
            "title": metadata.get("title") or debate["hypothesis"][:100],
            "question": debate["hypothesis"],
            "objective": metadata.get("objective", ""),
            "context": debate.get("context", ""),
            "project": metadata.get("project", "AGORA"),
            "supervisor": metadata.get("supervisor", "human-supervisor"),
            "relations": metadata.get("relations", {}),
            "protocol": {
                "configuration": debate["configuration"],
                "models": debate["models"],
                "mindsets": debate["mindsets"],
            },
            "observation": {
                "transcript": debate["transcript"],
                "retries": debate["retries"],
                "duration_seconds": debate["duration_seconds"],
            },
            "machine_judgment": debate["verdict"],
            "unknowns": metadata.get("unknowns", []),
            "supervisor_observations": [],
            "provenance": {
                "repository": "symbioticode/agora",
                "git_revision": self._git_revision(self.root.parent),
            },
            "sync": {"github": "LOCAL", "kbm": "NOT_SYNCHRONIZED"},
        }
        record["evidence_sha256"] = hashlib.sha256(canonical_json(record)).hexdigest()
        record["record_sha256"] = record_sha256(record)
        path = self.root / str(now.year) / f"{experiment_id}.json"
        self._atomic_write(path, record)
        return record

    def create_failed(self, experiment_id: str, metadata: dict, transcript: list, error: dict, now: datetime | None = None) -> dict:
        """Persist a failed experiment without pretending it has a verdict."""
        now = now or datetime.now(timezone.utc)
        record = {
            "schema_version": SCHEMA_VERSION,
            "id": experiment_id,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "status": "FAILED",
            "title": metadata.get("title") or metadata.get("question", "Expérience interrompue")[:100],
            "question": metadata.get("question", ""),
            "objective": metadata.get("objective", ""),
            "context": metadata.get("context", ""),
            "project": metadata.get("project", "AGORA"),
            "supervisor": metadata.get("supervisor", "human-supervisor"),
            "relations": metadata.get("relations", {}),
            "protocol": {"configuration": {"mode": "QUALIFIED", "rounds": 6}},
            "observation": {"transcript": transcript},
            "machine_judgment": None,
            "unknowns": ["Le jugement machine n'a pas été produit."],
            "supervisor_observations": [],
            "failure": error,
            "provenance": {"repository": "symbioticode/agora", "git_revision": self._git_revision(self.root.parent)},
            "sync": {"github": "LOCAL", "kbm": "NOT_SYNCHRONIZED"},
        }
        record["evidence_sha256"] = hashlib.sha256(canonical_json(record)).hexdigest()
        record["record_sha256"] = record_sha256(record)
        path = self.root / str(now.year) / f"{experiment_id}.json"
        self._atomic_write(path, record)
        return record

    def list(self) -> list[dict]:
        records = [json.loads(path.read_text(encoding="utf-8")) for path in self._paths()]
        return sorted(records, key=lambda item: item["id"], reverse=True)

    def get(self, experiment_id: str) -> dict:
        matches = list(self.root.glob(f"*/{experiment_id}.json"))
        if len(matches) != 1:
            raise KeyError(experiment_id)
        return json.loads(matches[0].read_text(encoding="utf-8"))

    def add_observation(self, experiment_id: str, actor: str, content: str) -> dict:
        if not content.strip():
            raise ValueError("L'observation est vide")
        matches = list(self.root.glob(f"*/{experiment_id}.json"))
        if len(matches) != 1:
            raise KeyError(experiment_id)
        path = matches[0]
        record = json.loads(path.read_text(encoding="utf-8"))
        record["supervisor_observations"].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "actor": actor or "human-supervisor",
            "content": content.strip(),
        })
        record["updated_at"] = datetime.now(timezone.utc).isoformat()
        record["record_sha256"] = record_sha256(record)
        self._atomic_write(path, record)
        return record

    def markdown(self, record: dict) -> str:
        verdict = record["machine_judgment"]
        lines = [
            "---",
            f"title: \"{record['id']} — {record['title'].replace(chr(34), chr(39))}\"",
            f"date: {record['created_at'][:10]}",
            "project: AGORA",
            f"status: {record['status']}",
            f"experiment_id: {record['id']}",
            f"source_revision: {record['provenance']['git_revision']}",
            f"source_sha256: {record['record_sha256']}",
            "tags:",
            "  - agora",
            "  - experience-supervisee",
            "  - connaissance",
            "  - ignorance",
            "---",
            "",
            f"# {record['id']} — {record['title']}",
            "",
            f"**Statut de l'expérience : {record['status']}**",
            "",
            "## Question",
            "",
            record["question"],
            "",
            "## Contexte",
            "",
            record["context"] or "Aucun contexte additionnel déclaré.",
            "",
            "## Échanges",
            "",
        ]
        for turn in record["observation"]["transcript"]:
            quoted = "\n".join(f"> {line}" if line else ">" for line in turn["content"].splitlines())
            lines.extend([f"### Tour {turn['round']} — Agent {turn['agent']}", "", quoted or "> *(réponse vide)*", ""])
        lines.extend(["## Jugement machine", ""])
        if verdict:
            lines.extend([f"- Verdict : **{verdict['verdict']}**", f"- Confiance : {verdict['confidence']}", f"- Juge : `{record['protocol']['models']['judge']}`", "", verdict.get("rationale") or verdict.get("reasoning", ""), ""])
        else:
            lines.extend(["Aucun verdict produit : expérience interrompue.", "", f"- Cause : `{record.get('failure', {}).get('code', 'UNKNOWN')}`", ""])
        lines.extend(["## Inconnues et limites", ""])
        lines.extend([f"- {item}" for item in record.get("unknowns", [])] or ["- Aucune inconnue explicitement ajoutée."])
        lines.extend(["", "## Observation du superviseur", ""])
        observations = record.get("supervisor_observations", [])
        lines.extend([f"- {item['content']} — `{item['actor']}`, {item['timestamp']}" for item in observations] or ["Aucune observation ajoutée."])
        lines.extend(["", "## Provenance", "", f"- Révision : `{record['provenance']['git_revision']}`", f"- SHA-256 de la preuve initiale : `{record['evidence_sha256']}`", f"- SHA-256 de l'enregistrement publié : `{record['record_sha256']}`", ""])
        return "\n".join(lines)
