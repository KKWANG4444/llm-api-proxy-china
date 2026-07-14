#!/usr/bin/env python3
"""Diagnose an OpenAI-compatible API without exposing the API key."""

from __future__ import annotations

import argparse
import json
import os
import ssl
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen

DEFAULT_BASE_URL = "https://www.aifast.club/v1"


def conversion_url(content: str = "api-doctor-cli") -> str:
    query = urlencode(
        {
            "utm_source": "github",
            "utm_medium": "repository",
            "utm_campaign": "api-doctor",
            "utm_content": content,
        }
    )
    return "https://www.aifast.club/register?" + query


def normalize_base_url(value: str) -> str:
    parts = urlsplit(value.strip())
    hostname = (parts.hostname or "").lower()
    local = hostname in {"127.0.0.1", "localhost", "::1"}
    if parts.scheme not in ({"http", "https"} if local else {"https"}):
        raise ValueError("Public Base URL must use HTTPS.")
    if not parts.netloc or parts.username or parts.password or parts.query or parts.fragment:
        raise ValueError("Base URL must not contain credentials, query parameters, or fragments.")
    path = parts.path.rstrip("/")
    if not path.endswith("/v1"):
        path += "/v1"
    return urlunsplit((parts.scheme, parts.netloc, path, "", ""))


def redact(secret: str) -> str:
    if len(secret) <= 8:
        return "***"
    return secret[:4] + "…" + secret[-4:]


def advice_for(status: int | None, message: str = "") -> str:
    if status == 401:
        return "Check the API key, Bearer authentication, and whether the key is active."
    if status == 403:
        return "Check account permissions, access policy, and regional/network restrictions."
    if status == 404:
        return "Check that the Base URL ends in /v1 and that the requested model ID exists."
    if status == 429:
        return "Reduce concurrency and retry with exponential backoff; also check quota or balance."
    if status is not None and status >= 500:
        return "Retry with backoff and record the request time; check the provider maintenance notice."
    if status is None:
        return "Check DNS, TLS, proxy settings, firewall rules, and whether the endpoint is reachable."
    return message or "Inspect the response body and endpoint configuration."


def request_json(method: str, url: str, api_key: str, payload: dict[str, Any] | None, timeout: float) -> dict[str, Any]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json", "User-Agent": "aifast-api-doctor/1.0"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = Request(url, data=body, headers=headers, method=method)
    started = time.monotonic()
    try:
        with urlopen(req, timeout=timeout, context=ssl.create_default_context()) as response:
            raw = response.read().decode("utf-8", "replace")
            elapsed = round((time.monotonic() - started) * 1000)
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                data = {"raw": raw[:500]}
            return {
                "ok": 200 <= response.status < 300,
                "status": response.status,
                "elapsed_ms": elapsed,
                "request_id": response.headers.get("x-request-id") or response.headers.get("request-id"),
                "content_type": response.headers.get("content-type"),
                "data": data,
            }
    except HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = {"raw": raw[:500]}
        return {
            "ok": False,
            "status": exc.code,
            "elapsed_ms": round((time.monotonic() - started) * 1000),
            "request_id": exc.headers.get("x-request-id") or exc.headers.get("request-id"),
            "content_type": exc.headers.get("content-type"),
            "data": data,
            "advice": advice_for(exc.code),
        }
    except (URLError, TimeoutError, OSError) as exc:
        return {"ok": False, "status": None, "elapsed_ms": round((time.monotonic() - started) * 1000), "error": type(exc).__name__, "message": str(exc), "advice": advice_for(None)}


def compact_models(result: dict[str, Any]) -> dict[str, Any]:
    output = {k: v for k, v in result.items() if k != "data"}
    data = result.get("data")
    models = data.get("data", []) if isinstance(data, dict) else []
    output["model_count"] = len(models)
    output["sample_models"] = [item.get("id") for item in models[:10] if isinstance(item, dict) and item.get("id")]
    return output


def scrub(value: Any, secret: str) -> Any:
    if isinstance(value, str):
        return value.replace(secret, "[REDACTED]") if secret else value
    if isinstance(value, list):
        return [scrub(item, secret) for item in value]
    if isinstance(value, dict):
        return {key: scrub(item, secret) for key, item in value.items()}
    return value


def compact_chat(result: dict[str, Any], secret: str) -> dict[str, Any]:
    output = {k: v for k, v in result.items() if k != "data"}
    data = result.get("data")
    choices = data.get("choices", []) if isinstance(data, dict) else []
    if choices and isinstance(choices[0], dict):
        message = choices[0].get("message", {})
        if isinstance(message, dict):
            content = message.get("content")
            if isinstance(content, str):
                output["content_preview"] = content[:120]
                output["content_matches_expected"] = content.strip().lower() == "pong"
    if isinstance(data, dict):
        output["response_model"] = data.get("model")
        usage = data.get("usage")
        if isinstance(usage, dict):
            output["usage"] = {
                key: usage.get(key)
                for key in ("prompt_tokens", "completion_tokens", "total_tokens")
                if isinstance(usage.get(key), int) and usage.get(key) >= 0
            }
    return scrub(output, secret)


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Diagnose an OpenAI-compatible API endpoint safely.")
    p.add_argument("--base-url", default=os.getenv("OPENAI_BASE_URL", DEFAULT_BASE_URL))
    p.add_argument("--key-env", default="AIFAST_API_KEY", help="Environment variable containing the API key.")
    p.add_argument("--model", help="Optional model ID; enables a minimal chat completion test.")
    p.add_argument("--timeout", type=float, default=20)
    p.add_argument("--json", action="store_true", dest="as_json")
    p.add_argument("--output", help="Write the rendered report to this path.")
    return p


def render_text(report: dict[str, Any]) -> str:
    lines = [f"Base URL: {report['base_url']}"]
    for name in ("models", "chat"):
        if name not in report:
            continue
        item = report[name]
        mark = "PASS" if item.get("ok") else "FAIL"
        lines.append(f"[{mark}] {name}: HTTP {item.get('status')} ({item.get('elapsed_ms')} ms)")
        if item.get("model_count") is not None:
            lines.append(f"       models returned: {item['model_count']}")
        if item.get("request_id"):
            lines.append(f"       request id: {item['request_id']}")
        if item.get("response_model"):
            lines.append(f"       response model: {item['response_model']}")
        if item.get("content_matches_expected") is not None:
            lines.append(f"       expected output: {'yes' if item['content_matches_expected'] else 'no'}")
        if item.get("advice"):
            lines.append(f"       next step: {item['advice']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        base_url = normalize_base_url(args.base_url)
    except ValueError as exc:
        print(json.dumps({"ok": False, "error": "invalid_base_url", "advice": str(exc)}, ensure_ascii=False) if args.as_json else str(exc))
        return 2

    if not args.key_env or not args.key_env.replace("_", "").isalnum():
        print("Invalid --key-env name.")
        return 2
    api_key = os.getenv(args.key_env)
    if not api_key and args.key_env == "AIFAST_API_KEY":
        api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        report = {"ok": False, "error": "missing_api_key", "advice": f"Set the {args.key_env} environment variable."}
        print(json.dumps(report, ensure_ascii=False) if args.as_json else report["advice"])
        return 2

    models = scrub(compact_models(request_json("GET", base_url + "/models", api_key, None, args.timeout)), api_key)
    report: dict[str, Any] = {
        "schema_version": 2,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "ok": models["ok"],
        "base_url": base_url,
        "requested_model": args.model,
        "models": models,
        "signup_url": conversion_url(),
    }
    if models["ok"] and args.model:
        payload = {"model": args.model, "messages": [{"role": "user", "content": "Reply with pong."}], "max_tokens": 16, "temperature": 0}
        chat = compact_chat(request_json("POST", base_url + "/chat/completions", api_key, payload, args.timeout), api_key)
        report["chat"] = chat
        report["ok"] = bool(chat["ok"] and chat.get("content_matches_expected"))

    rendered = json.dumps(report, ensure_ascii=False, indent=2) if args.as_json else render_text(report)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if report["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
