import importlib.util
import json
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "tools" / "aifast_api_doctor.py"


def load_module():
    spec = importlib.util.spec_from_file_location("aifast_api_doctor", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeAPI(BaseHTTPRequestHandler):
    mode = "ok"

    def log_message(self, *_args):
        pass

    def send_json(self, status, payload):
        data = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/v1/models":
            if self.headers.get("Authorization") != "Bearer test-key":
                self.send_json(401, {"error": {"message": "bad key"}})
            elif self.mode == "rate_limit":
                self.send_json(429, {"error": {"message": "slow down"}})
            else:
                self.send_json(200, {"data": [{"id": "demo-model"}]})
        else:
            self.send_json(404, {"error": {"message": "not found"}})

    def do_POST(self):
        if self.path != "/v1/chat/completions":
            self.send_json(404, {"error": {"message": "not found"}})
            return
        if self.headers.get("Authorization") != "Bearer test-key":
            self.send_json(401, {"error": {"message": "bad key"}})
            return
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))))
        if body.get("model") != "demo-model":
            self.send_json(404, {"error": {"message": "model missing"}})
            return
        self.send_json(200, {"choices": [{"message": {"content": "pong"}}]})


class Server:
    def __enter__(self):
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), FakeAPI)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        return f"http://127.0.0.1:{self.httpd.server_port}/v1"

    def __exit__(self, *_args):
        self.httpd.shutdown()
        self.thread.join()


def test_normalize_base_url():
    m = load_module()
    assert m.normalize_base_url("https://example.com/") == "https://example.com/v1"
    assert m.normalize_base_url("https://example.com/v1/") == "https://example.com/v1"


def test_redacts_api_keys():
    m = load_module()
    assert m.redact("sk-1234567890") == "sk-1…7890"
    assert "1234567890" not in m.redact("sk-1234567890")


def test_conversion_url_is_attributed_without_secrets():
    m = load_module()
    url = m.conversion_url("github-readme-cn")
    assert url.startswith("https://www.aifast.club/register?")
    assert "utm_source=github" in url
    assert "utm_campaign=api-doctor" in url
    assert "api_key" not in url.lower()


def test_successful_models_and_chat_diagnosis():
    with Server() as base:
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--base-url", base, "--api-key", "test-key", "--model", "demo-model", "--json"],
            text=True,
            capture_output=True,
        )
    assert proc.returncode == 0, proc.stderr
    report = json.loads(proc.stdout)
    assert report["models"]["status"] == 200
    assert report["chat"]["status"] == 200
    assert report["chat"]["content"] == "pong"
    assert "utm_source=github" in report["signup_url"]
    assert "test-key" not in proc.stdout


def test_auth_error_returns_actionable_nonzero_result():
    with Server() as base:
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--base-url", base, "--api-key", "wrong", "--json"],
            text=True,
            capture_output=True,
        )
    assert proc.returncode == 2
    report = json.loads(proc.stdout)
    assert report["models"]["status"] == 401
    assert "API key" in report["models"]["advice"]
    assert "wrong" not in proc.stdout


def test_missing_key_is_reported_without_network_call():
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--base-url", "http://127.0.0.1:1/v1", "--json"],
        text=True,
        capture_output=True,
    )
    assert proc.returncode == 2
    report = json.loads(proc.stdout)
    assert report["error"] == "missing_api_key"


def test_rate_limit_has_retry_advice():
    FakeAPI.mode = "rate_limit"
    try:
        with Server() as base:
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), "--base-url", base, "--api-key", "test-key", "--json"],
                text=True,
                capture_output=True,
            )
    finally:
        FakeAPI.mode = "ok"
    assert proc.returncode == 2
    report = json.loads(proc.stdout)
    assert report["models"]["status"] == 429
    assert "retry" in report["models"]["advice"].lower()
