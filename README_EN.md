# OpenAI-compatible AI API setup for China and international users

[![中文](https://img.shields.io/badge/中文-README-red)](README.md)
[![Website](https://img.shields.io/badge/Website-www.aifast.club-FF6B35)](https://www.aifast.club)
[![Catalog](https://img.shields.io/badge/Models-current_catalog-blue)](https://www.aifast.club)

This guide shows how to connect an OpenAI-compatible client to AIFast without tying your application to one model vendor. It does not claim a fixed model count, latency, uptime, or automatic failover. Test the exact model and workload you plan to run.

## Quick start

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://www.aifast.club/v1",
    api_key=os.environ["AIFAST_API_KEY"],
)

response = client.chat.completions.create(
    model="claude-sonnet-5",
    messages=[{"role": "user", "content": "Explain idempotency in APIs."}],
)

print(response.choices[0].message.content)
```

The `/v1/models` endpoint requires authentication. A public catalog entry alone does not prove that a model is online, so check the console and current maintenance notices before deployment.

## Model IDs verified in the public catalog

The following examples were checked against the public AIFast configuration on 2026-07-13:

| Provider | Example IDs |
|:---|:---|
| OpenAI | `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna` |
| Anthropic | `claude-sonnet-5`, `claude-opus-4-8`, `claude-fable-5` |
| xAI | `grok-4.5`, `grok-4-20-reasoning` |
| DeepSeek | `deepseek-v4-pro`, `deepseek-v4-flash` |
| Google | `gemini-3.5-flash`, `gemini-3.1-pro-preview` |
| Alibaba | `qwen3.7-max`, `qwen3.7-plus` |
| Zhipu | `glm-5.2` |
| Moonshot | `kimi-k2.7-code` |

This is a sample, not an availability promise. Model configuration and maintenance status change independently.

## Tool configuration

### Cursor, Dify, Open WebUI and similar clients

Use the client's OpenAI-compatible provider option:

| Field | Value |
|:---|:---|
| Base URL | `https://www.aifast.club/v1` |
| API key | Your AIFast key |
| Model | An exact ID from the current console |

Start with a short text request. Add tools, images, streaming, and structured output one feature at a time. This makes compatibility failures easier to isolate.

### Claude Code

Anthropic documents `ANTHROPIC_BASE_URL` and `ANTHROPIC_AUTH_TOKEN` for gateway configuration. A third-party gateway still needs to support the Anthropic request format expected by your Claude Code version.

```bash
export ANTHROPIC_BASE_URL="https://www.aifast.club/v1"
export ANTHROPIC_AUTH_TOKEN="$AIFAST_API_KEY"
claude
```

If this fails, save the HTTP status and response body before changing several settings at once.

### Codex CLI

Codex supports custom providers through its configuration. The exact keys can change between releases, so use the current OpenAI Codex configuration reference rather than copying an old environment-variable name.

## Payment

Payment rules differ by account region:

- International users can pay only with cryptocurrency.
- **1 AIFast balance dollar ("1 刀") = 0.07 USDC or 0.07 USDT.**
- Fiat payment is not available to international users.
- Domestic account options are shown separately in the console.

Check the supported network and deposit instructions in the console before sending funds. Do not infer a blockchain network from the token symbol alone. This is an AIFast balance-unit conversion. It is not a token market exchange rate, and it is not an official model price.

## Production checks

Before moving traffic, record:

1. the exact model ID and request format;
2. HTTP status and response body for failed requests;
3. p50 and p95 latency from your deployment region;
4. streaming and tool-call behavior;
5. your own retry, rate-limit, and fallback policy.

A gateway should not silently replace one model with another. If your application needs fallback, define compatible groups in your own application and log which model served each request.

## Common errors

### 401

Check the `Authorization: Bearer ***` header, account balance, and whether the key is active.

### 404 or model not found

Use the exact model ID shown in the console. Display names and API IDs are not interchangeable.

### 429

Back off with jitter. Do not retry immediately in a tight loop.

### 5xx or timeout

Retry only idempotent requests, cap the number of attempts, and preserve the original error for debugging.

## Links

- [AIFast model catalog and console](https://www.aifast.club)
- [Integration guide](https://github.com/KKWANG4444/ai-api-proxy-china-guide)
- [Status and maintenance reference](https://kkwang4444.github.io/api-status/)
- [中文说明](README.md)
