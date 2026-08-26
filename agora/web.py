"""Loopback-only HTTP adapter for supervised AGORA experiments."""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import threading
import uuid
import traceback
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from dotenv import load_dotenv

from .engine import DEFAULT_ROUNDS, MODEL_A, MODEL_B, DebateEngine
from .registry import ExperimentRegistry

REPO = Path(__file__).resolve().parent.parent
DIST = REPO / "ui" / "dist"
RUN_ROOT = REPO / "runtime" / "runs"
MAX_BODY = 32_768
EXPERIMENT_ID = re.compile(r"^AGO-EXP-\d{4}-\d{4}$")


def _runtime_mode(engine: DebateEngine) -> str:
    ready = engine.gateway.ready() if hasattr(engine.gateway, "ready") else True
    return "REQUALIFICATION_REQUIRED" if ready else "EXECUTION_SUSPENDED"


def _public_record(record: dict, summary: bool = False) -> dict:
    if not summary:
        return record
    return {
        "id": record["id"],
        "created_at": record["created_at"],
        "title": record["title"],
        "question": record["question"],
        "status": record["status"],
        "verdict": record["machine_judgment"],
        "sync": record["sync"],
        "evidence_sha256": record["evidence_sha256"],
    }


def make_handler(engine: DebateEngine, registry: ExperimentRegistry, dist: Path = DIST, run_root: Path = RUN_ROOT):
    runs = {}
    runs_lock = threading.Lock()
    run_root.mkdir(parents=True, exist_ok=True)

    def persist(state: dict):
        registry._atomic_write(run_root / f"{state['run_id']}.json", state)

    for path in run_root.glob("*.json"):
        try:
            state = json.loads(path.read_text(encoding="utf-8"))
            if state.get("status") == "RUNNING":
                error = {"code": "SERVICE_RESTART_DURING_RUN", "message": "Le service a redémarré pendant l'expérience; le run partiel a été conservé."}
                try:
                    failed = registry.get(state["experiment_id"])
                except KeyError:
                    failed = registry.create_failed(state["experiment_id"], state.get("request", {}), state.get("transcript", []), error)
                state.update({"status": "FAILED", "stage": "FAILED", "error": error["message"], "experiment": failed})
                persist(state)
            runs[state["run_id"]] = state
        except (OSError, ValueError, KeyError):
            continue

    def launch(body: dict) -> dict:
        experiment_id = registry.reserve_id()
        run_id = uuid.uuid4().hex
        state = {"run_id": run_id, "experiment_id": experiment_id, "status": "RUNNING", "stage": "DEBATE", "transcript": [], "request": body.copy()}
        try:
            persist(state)
        except Exception as exc:
            error = {"code": "RUNTIME_PERSISTENCE_ERROR", "message": (str(exc).strip() or type(exc).__name__)[:500]}
            failed = registry.create_failed(experiment_id, body, [], error)
            state.update({"status": "FAILED", "stage": "FAILED", "error": error["message"], "experiment": failed})
            with runs_lock:
                runs[run_id] = state
            return state.copy()
        with runs_lock:
            runs[run_id] = state

        def event(item):
            with runs_lock:
                if item["type"] == "turn":
                    state["transcript"].append(item["turn"])
                elif item["type"] == "judge":
                    state["stage"] = "JUDGMENT"
                persist(state)

        def worker():
            try:
                debate = engine.run(body.get("question", ""), context=body.get("context", ""), on_event=event)
                record = registry.create(debate, body, experiment_id=experiment_id)
                with runs_lock:
                    state.update({"status": "COMPLETED", "stage": "COMPLETED", "experiment": record})
                    persist(state)
            except Exception as exc:
                detail = str(exc).strip() or type(exc).__name__
                error = {"code": type(exc).__name__, "message": detail[:500]}
                failed = registry.create_failed(experiment_id, body, state["transcript"], error)
                print(json.dumps({"component": "agora-run", "run_id": run_id, "experiment_id": experiment_id, "error": error, "traceback": traceback.format_exc(limit=5)}, ensure_ascii=False))
                with runs_lock:
                    state.update({"status": "FAILED", "stage": "FAILED", "error": detail[:500], "experiment": failed})
                    persist(state)

        threading.Thread(target=worker, name=f"agora-{run_id[:8]}", daemon=True).start()
        return state.copy()

    class Handler(BaseHTTPRequestHandler):
        server_version = "AGORA/0.2"

        def log_message(self, fmt, *args):
            print(json.dumps({"component": "agora-web", "client": self.client_address[0], "message": fmt % args}))

        def _json(self, status: int, data: dict | list):
            payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(payload)

        def _error(self, status: int, code: str, message: str):
            self._json(status, {"error": {"code": code, "message": message}})

        def _body(self) -> dict:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_BODY:
                raise ValueError(f"Corps requis, taille maximale {MAX_BODY} octets")
            try:
                body = json.loads(self.rfile.read(length).decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ValueError("JSON invalide") from exc
            if not isinstance(body, dict):
                raise ValueError("Un objet JSON est requis")
            return body

        def _local_origin(self) -> bool:
            origin = self.headers.get("Origin")
            if not origin:
                return True
            parsed = urlparse(origin)
            return parsed.hostname in {"127.0.0.1", "localhost"}

        def do_GET(self):
            parsed = urlparse(self.path)
            path = parsed.path
            if path == "/health":
                provider_status = engine.gateway.status() if hasattr(engine.gateway, "status") else {}
                active = sum(1 for item in runs.values() if item.get("status") == "RUNNING")
                return self._json(200, {"status": "ok", "service": "agora-web", "mode": _runtime_mode(engine), "historical_protocol_qualification": "VALIDATED_FOR_SUPERVISED_RESEARCH", "current_configuration_qualification": "REQUIRED", "schema": "1.0", "active_runs": active, "providers": provider_status})
            if path == "/api/v1/config":
                return self._json(200, {
                    "mode": _runtime_mode(engine),
                    "historical_protocol_qualification": "VALIDATED_FOR_SUPERVISED_RESEARCH",
                    "current_configuration_qualification": "REQUIRED",
                    "rounds": DEFAULT_ROUNDS,
                    "agents": {
                        "A": {"provider": "anthropic", "model": MODEL_A, "mindset": "empiricist"},
                        "B": {"provider": "deepseek", "model": MODEL_B, "mindset": "rationalist"},
                    },
                    "providers": engine.gateway.status() if hasattr(engine.gateway, "status") else {},
                    "action_authority": "NONE",
                    "factual_reliability": "NOT_GENERALLY_QUALIFIED",
                })
            if path == "/api/v1/experiments":
                query = parse_qs(parsed.query)
                records = registry.list()
                if query.get("q"):
                    needle = query["q"][0].lower()
                    records = [r for r in records if needle in (r["id"] + " " + r["question"] + " " + r["title"]).lower()]
                return self._json(200, [_public_record(item, summary=True) for item in records])
            if path == "/api/v1/sync":
                sync_path = REPO / "sync" / "manifest.json"
                if not sync_path.exists():
                    return self._json(200, {"status": "NOT_SYNCHRONIZED", "github": "UNKNOWN", "kbm": "UNKNOWN"})
                return self._json(200, json.loads(sync_path.read_text(encoding="utf-8")))
            run_match = re.fullmatch(r"/api/v1/runs/([a-f0-9]{32})", path)
            if run_match:
                with runs_lock:
                    state = runs.get(run_match.group(1))
                    payload = json.loads(json.dumps(state, ensure_ascii=False)) if state else None
                if not payload:
                    return self._error(404, "NOT_FOUND", "Run inconnu")
                return self._json(200, payload)
            match = re.fullmatch(r"/api/v1/experiments/(AGO-EXP-\d{4}-\d{4})(/export)?", path)
            if match:
                try:
                    record = registry.get(match.group(1))
                except KeyError:
                    return self._error(404, "NOT_FOUND", "Expérience inconnue")
                if match.group(2):
                    fmt = parse_qs(parsed.query).get("format", ["json"])[0]
                    if fmt == "markdown":
                        payload = registry.markdown(record).encode("utf-8")
                        self.send_response(200)
                        self.send_header("Content-Type", "text/markdown; charset=utf-8")
                        self.send_header("Content-Disposition", f'attachment; filename="{record["id"]}.md"')
                        self.send_header("Content-Length", str(len(payload)))
                        self.end_headers()
                        return self.wfile.write(payload)
                    return self._json(200, record)
                return self._json(200, record)
            return self._static(path)

        def do_POST(self):
            if not self._local_origin():
                return self._error(403, "ORIGIN_REFUSED", "Origine non locale")
            try:
                body = self._body()
                if self.path == "/api/v1/providers/probe":
                    if not hasattr(engine.gateway, "probe"):
                        return self._error(501, "PROBE_UNAVAILABLE", "La gateway ne fournit pas de diagnostic")
                    requested = body.get("providers", ["anthropic", "deepseek"])
                    if not isinstance(requested, list) or not requested or set(requested) - {"anthropic", "deepseek"}:
                        raise ValueError("providers doit contenir anthropic et/ou deepseek")
                    results = [engine.gateway.probe(provider) for provider in requested]
                    return self._json(200, {"kind": "TRANSPORT_DIAGNOSTIC", "creates_experiment": False, "ready": engine.gateway.ready(), "results": results})
                if self.path == "/api/v1/experiments":
                    if hasattr(engine.gateway, "ready") and not engine.gateway.ready():
                        return self._error(409, "EXECUTION_SUSPENDED", "Un provider n'a pas franchi le diagnostic; aucun identifiant ni appel de débat n'a été créé")
                    allowed = {"question", "context", "title", "objective", "supervisor", "relations", "unknowns"}
                    unknown = set(body) - allowed
                    if unknown:
                        raise ValueError(f"Champs inconnus: {', '.join(sorted(unknown))}")
                    question = body.get("question", "").strip()
                    if not question:
                        raise ValueError("L'hypothèse est obligatoire")
                    return self._json(HTTPStatus.ACCEPTED, launch(body))
                match = re.fullmatch(r"/api/v1/experiments/(AGO-EXP-\d{4}-\d{4})/observations", self.path)
                if match:
                    record = registry.add_observation(match.group(1), body.get("actor", ""), body.get("content", ""))
                    return self._json(200, record)
                return self._error(404, "NOT_FOUND", "Route inconnue")
            except KeyError:
                return self._error(404, "NOT_FOUND", "Expérience inconnue")
            except ValueError as exc:
                return self._error(400, "INVALID_REQUEST", str(exc))
            except Exception as exc:
                self.log_error("experiment failed: %s", type(exc).__name__)
                return self._error(502, "PROVIDER_FAILURE", "L'expérience n'a pas pu être exécutée")

        def _static(self, path: str):
            relative = "index.html" if path == "/" else path.lstrip("/")
            target = (dist / relative).resolve()
            if dist.resolve() not in target.parents or not target.is_file():
                return self._error(404, "NOT_FOUND", "Ressource inconnue")
            payload = target.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", mimetypes.guess_type(target.name)[0] or "application/octet-stream")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(payload)

    return Handler


def create_server(host="127.0.0.1", port=8768, engine=None, registry=None, dist=DIST, run_root=RUN_ROOT):
    if host not in {"127.0.0.1", "localhost"}:
        raise ValueError("AGORA web doit rester sur l'interface loopback")
    registry = registry or ExperimentRegistry(REPO / "experiments")
    engine = engine or DebateEngine(judge_selector=lambda: "deepseek" if len(registry.list()) % 2 == 0 else "anthropic")
    records = registry.list()
    if records and hasattr(engine.gateway, "restore_from_experiment"):
        for record in reversed(records):
            engine.gateway.restore_from_experiment(record)
    return ThreadingHTTPServer((host, port), make_handler(engine, registry, dist, run_root))


def main():
    load_dotenv(REPO / ".env")
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8768)
    args = parser.parse_args()
    server = create_server(args.host, args.port)
    print(json.dumps({"service": "agora-web", "listen": f"http://{args.host}:{args.port}"}))
    server.serve_forever()


if __name__ == "__main__":
    main()
