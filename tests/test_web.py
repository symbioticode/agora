import json
import threading
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from agora.engine import DebateEngine
from agora.registry import ExperimentRegistry
from agora.web import create_server
from tests.test_engine import FakeGateway


def request(base, path, method="GET", data=None, origin=None):
    headers = {}
    payload = None
    if data is not None:
        payload = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if origin:
        headers["Origin"] = origin
    req = Request(base + path, data=payload, method=method, headers=headers)
    with urlopen(req, timeout=3) as response:
        body = response.read()
        return response.status, response.headers, body


def test_web_api_without_network(tmp_path):
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("<h1>AGORA</h1>", encoding="utf-8")
    registry = ExperimentRegistry(tmp_path / "experiments")
    engine = DebateEngine(FakeGateway(), judge_selector=lambda: "deepseek")
    server = create_server(port=0, engine=engine, registry=registry, dist=dist, run_root=tmp_path / "runs")
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        assert json.loads(request(base, "/health")[2])["status"] == "ok"
        assert json.loads(request(base, "/api/v1/config")[2])["rounds"] == 6
        status, _, body = request(base, "/api/v1/experiments", "POST", {"question": "Question test", "title": "Test"})
        assert status == 202
        run = json.loads(body)
        for _ in range(30):
            run = json.loads(request(base, f"/api/v1/runs/{run['run_id']}")[2])
            if run["status"] != "RUNNING":
                break
            time.sleep(0.02)
        assert run["status"] == "COMPLETED"
        experiment = run["experiment"]
        assert experiment["id"] == "AGO-EXP-2026-0001"
        listing = json.loads(request(base, "/api/v1/experiments")[2])
        assert listing[0]["id"] == experiment["id"]
        markdown = request(base, f"/api/v1/experiments/{experiment['id']}/export?format=markdown")[2]
        assert experiment["id"].encode() in markdown
        assert b"AGORA" in request(base, "/")[2]
    finally:
        server.shutdown()
        server.server_close()


def test_web_refuses_non_local_origin(tmp_path):
    registry = ExperimentRegistry(tmp_path / "experiments")
    server = create_server(port=0, engine=DebateEngine(FakeGateway()), registry=registry, dist=tmp_path, run_root=tmp_path / "runs")
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base = f"http://127.0.0.1:{server.server_port}"
        try:
            request(base, "/api/v1/experiments", "POST", {"question": "x"}, "https://evil.example")
        except HTTPError as exc:
            assert exc.code == 403
        else:
            raise AssertionError("external origin accepted")
    finally:
        server.shutdown()
        server.server_close()


def test_running_state_is_recovered_as_failed_after_restart(tmp_path):
    registry = ExperimentRegistry(tmp_path / "experiments")
    experiment_id = registry.reserve_id()
    run_root = tmp_path / "runs"
    run_root.mkdir()
    run_id = "a" * 32
    (run_root / f"{run_id}.json").write_text(json.dumps({
        "run_id": run_id,
        "experiment_id": experiment_id,
        "status": "RUNNING",
        "stage": "DEBATE",
        "request": {"question": "Question interrompue"},
        "transcript": [{"round": 0, "agent": "A", "content": "partiel"}],
    }), encoding="utf-8")
    server = create_server(port=0, engine=DebateEngine(FakeGateway()), registry=registry, dist=tmp_path, run_root=run_root)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base = f"http://127.0.0.1:{server.server_port}"
        recovered = json.loads(request(base, f"/api/v1/runs/{run_id}")[2])
        assert recovered["status"] == "FAILED"
        assert registry.get(experiment_id)["failure"]["code"] == "SERVICE_RESTART_DURING_RUN"
    finally:
        server.shutdown()
        server.server_close()


def test_persistence_failure_creates_failed_experiment(tmp_path, monkeypatch):
    registry = ExperimentRegistry(tmp_path / "experiments")
    original = registry._atomic_write
    def fail_only_runs(path, data):
        if "runs" in path.parts:
            raise PermissionError("runtime read-only")
        return original(path, data)
    monkeypatch.setattr(registry, "_atomic_write", fail_only_runs)
    server = create_server(port=0, engine=DebateEngine(FakeGateway()), registry=registry, dist=tmp_path, run_root=tmp_path / "runs")
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base = f"http://127.0.0.1:{server.server_port}"
        status, _, body = request(base, "/api/v1/experiments", "POST", {"question": "Question"})
        assert status == 202
        run = json.loads(body)
        assert run["status"] == "FAILED"
        assert run["experiment"]["failure"]["code"] == "RUNTIME_PERSISTENCE_ERROR"
    finally:
        server.shutdown()
        server.server_close()


def test_suspended_gateway_refuses_run_without_reserving_experiment(tmp_path):
    class SuspendedGateway(FakeGateway):
        def ready(self):
            return False
        def status(self):
            return {"anthropic": {"status": "ON"}, "deepseek": {"status": "DEGRADED"}}

    registry = ExperimentRegistry(tmp_path / "experiments")
    server = create_server(port=0, engine=DebateEngine(SuspendedGateway()), registry=registry, dist=tmp_path, run_root=tmp_path / "runs")
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base = f"http://127.0.0.1:{server.server_port}"
        try:
            request(base, "/api/v1/experiments", "POST", {"question": "Question"})
        except HTTPError as exc:
            assert exc.code == 409
            assert json.loads(exc.read())["error"]["code"] == "EXECUTION_SUSPENDED"
        else:
            raise AssertionError("suspended execution accepted")
        assert registry.list() == []
    finally:
        server.shutdown()
        server.server_close()


def test_probe_is_diagnostic_and_never_creates_experiment(tmp_path):
    class ProbeGateway(FakeGateway):
        available = False
        def ready(self):
            return self.available
        def status(self):
            status = "ON" if self.available else "DEGRADED"
            return {"anthropic": {"status": status}, "deepseek": {"status": status}}
        def probe(self, provider):
            self.available = True
            return {"provider": provider, "ok": True, "content_present": True, "retries": 0}

    registry = ExperimentRegistry(tmp_path / "experiments")
    server = create_server(port=0, engine=DebateEngine(ProbeGateway()), registry=registry, dist=tmp_path, run_root=tmp_path / "runs")
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base = f"http://127.0.0.1:{server.server_port}"
        status, _, body = request(base, "/api/v1/providers/probe", "POST", {"providers": ["deepseek"]})
        diagnostic = json.loads(body)
        assert status == 200
        assert diagnostic["kind"] == "TRANSPORT_DIAGNOSTIC"
        assert diagnostic["creates_experiment"] is False
        assert diagnostic["ready"] is True
        assert registry.list() == []
    finally:
        server.shutdown()
        server.server_close()
