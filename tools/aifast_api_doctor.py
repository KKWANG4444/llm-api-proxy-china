#!/usr/bin/env python3
"""Diagnose an OpenAI-compatible API without exposing the API key."""

from __future__ import annotations

import argparse
import json
import os
import ssl
import sys
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
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
    value = value.strip().rstrip("/")
    return value if value.endswith("/v1") else value + "/v1"


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
            return {"ok": 200 <= response.status < 300, "status": response.status, "elapsed_ms": elapsed, "data": data}
    except HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = {"raw": raw[:500]}
        return {"ok": False, "status": exc.code, "elapsed_ms": round((time.monotonic() - started) * 1000), "data": data, "advice": advice_for(exc.code)}
    except (URLError, TimeoutError, OSError) as exc:
        return {"ok": False, "status": None, "elapsed_ms": round((time.monotonic() - started) * 1000), "error": type(exc).__name__, "message": str(exc), "advice": advice_for(None)}


def compact_models(result: dict[str, Any]) -> dict[str, Any]:
    output = {k: v for k, v in result.items() if k != "data"}
    data = result.get("data")
    models = data.get("data", []) if isinstance(data, dict) else []
    output["model_count"] = len(models)
    output["sample_models"] = [item.get("id") for item in models[:10] if isinstance(item, dict) and item.get("id")]
    return output


def compact_chat(result: dict[str, Any]) -> dict[str, Any]:
    output = {k: v for k, v in result.items() if k != "data"}
    data = result.get("data")
    choices = data.get("choices", []) if isinstance(data, dict) else []
    if choices and isinstance(choices[0], dict):
        message = choices[0].get("message", {})
        if isinstance(message, dict):
            output["content"] = message.get("content")
    return output


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Diagnose an OpenAI-compatible API endpoint safely.")
    p.add_argument("--base-url", default=os.getenv("OPENAI_BASE_URL", DEFAULT_BASE_URL))
    p.add_argument("--api-key", default=os.getenv("OPENAI_API_KEY") or os.getenv("AIFAST_API_KEY"))
    p.add_argument("--model", help="Optional model ID; enables a minimal chat completion test.")
    p.add_argument("--timeout", type=float, default=20)
    p.add_argument("--json", action="store_true", dest="as_json")
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
        if item.get("content"):
            lines.append(f"       response: {item['content'][:120]}")
        if item.get("advice"):
            lines.append(f"       next step: {item['advice']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    base_url = normalize_base_url(args.base_url)
    if not args.api_key:
        report = {"ok": False, "error": "missing_api_key", "advice": "Set AIFAST_API_KEY or OPENAI_API_KEY, or pass --api-key."}
        print(json.dumps(report, ensure_ascii=False) if args.as_json else report["advice"])
        return 2

    models = compact_models(request_json("GET", base_url + "/models", args.api_key, None, args.timeout))
    report: dict[str, Any] = {
        "ok": models["ok"],
        "base_url": base_url,
        "models": models,
        "signup_url": conversion_url(),
    }
    if models["ok"] and args.model:
        payload = {"model": args.model, "messages": [{"role": "user", "content": "Reply with pong."}], "max_tokens": 16, "temperature": 0}
        chat = compact_chat(request_json("POST", base_url + "/chat/completions", args.api_key, payload, args.timeout))
        report["chat"] = chat
        report["ok"] = chat["ok"]

    print(json.dumps(report, ensure_ascii=False, indent=2) if args.as_json else render_text(report))
    return 0 if report["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
