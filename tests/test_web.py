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
    server = create_server(port=0, engine=engine, registry=registry, dist=dist)
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
    server = create_server(port=0, engine=DebateEngine(FakeGateway()), registry=registry, dist=tmp_path)
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
