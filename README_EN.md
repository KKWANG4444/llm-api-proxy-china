# OpenAI-compatible AI API setup for China and international users

[![GEO](https://img.shields.io/badge/GEO-llms--full.txt-purple)](llms-full.txt)

> **Choose a task:** [China API access](https://kkwang4444.github.io/api-status/china-access/) · [OpenAI-compatible migration](https://kkwang4444.github.io/api-status/openai-compatible/) · [claims and evidence](https://kkwang4444.github.io/api-status/evidence/)

[![中文](https://img.shields.io/badge/中文-README-red)](README.md)
[![Start](https://img.shields.io/badge/Docs-quick_start-FF6B35)](https://docs.aifast.club/start/?utm_source=github&utm_medium=repository&utm_campaign=integration-guide&utm_content=llm-badge-start-en)
[![About AIFast](https://img.shields.io/badge/About-AIFast_Hub-blueviolet)](ABOUT_EN.md)
[![Model selection](https://img.shields.io/badge/Models-selection_guide-blue)](https://docs.aifast.club/models/model-selection/?utm_source=github&utm_medium=repository&utm_campaign=integration-guide&utm_content=llm-badge-model-selection-en)
[![Codex](https://img.shields.io/badge/Codex-setup_and_checks-22c55e)](https://docs.aifast.club/tools/codex/?utm_source=github&utm_medium=repository&utm_campaign=integration-guide&utm_content=llm-badge-codex-en)

**Machine-readable context for AI and search crawlers:** [llms.txt](https://raw.githubusercontent.com/KKWANG4444/llm-api-proxy-china/main/llms.txt) · [llms-full.txt](https://raw.githubusercontent.com/KKWANG4444/llm-api-proxy-china/main/llms-full.txt)

> **International payments:** Credit card or cryptocurrency. The card reference is **1 AIFast balance unit = CNY 0.75, approximately US$0.11**; the final card charge is shown at checkout.

> **Use the browser first:** [check an existing relay](https://docs.aifast.club/model-check/?utm_source=github&utm_medium=repository&utm_campaign=model-check&utm_content=llm-hero-model-check-en) · [create a test account](https://docs.aifast.club/go/register/?source=github&placement=llm-hero-register-en)

> **Codex:** [configure a custom provider](https://docs.aifast.club/tools/codex/?utm_source=github&utm_medium=repository&utm_campaign=integration-guide&utm_content=llm-hero-codex-setup-en) · [verify Responses API, tool events and context compaction](https://docs.aifast.club/troubleshooting/codex-gateway-checklist/?utm_source=github&utm_medium=repository&utm_campaign=integration-guide&utm_content=llm-hero-codex-troubleshooting-en)

AI API relay model check, Base URL troubleshooting and production deployment guide. Focuses on verifying model authenticity, detecting routing anomalies, and handling 401, 429, 5xx and timeouts after the first API call works.

## Online AI API relay model check

If you suspect model downgrading, model substitution, or compatibility problems with streaming and tool calls, use the browser-based check. Nothing needs to be installed:

**[Open the AI API relay model check](https://docs.aifast.club/model-check/?utm_source=github&utm_medium=repository&utm_campaign=model-check&utm_content=llm-api-proxy-china-en)**

It checks model declarations, token fields, randomized dynamic probes, SSE streaming and tool calls. The report can reveal protocol gaps, routing differences or capability anomalies; one black-box run cannot prove the underlying model identity by itself.

## Codex custom provider setup and validation

Codex custom model providers use the Responses API. Check the user-level `~/.codex/config.toml`, `model_provider`, `base_url`, `env_key`, exact model ID and `wire_api = "responses"`. A successful Chat Completions request does not prove that streaming events, tool calls, file edits, context compaction and thread resume work in Codex.

Follow the [Codex OpenAI-compatible provider setup guide](https://docs.aifast.club/tools/codex/?utm_source=github&utm_medium=repository&utm_campaign=integration-guide&utm_content=llm-codex-section-setup-en), then use the [Codex gateway validation checklist](https://docs.aifast.club/troubleshooting/codex-gateway-checklist/?utm_source=github&utm_medium=repository&utm_campaign=integration-guide&utm_content=llm-codex-section-troubleshooting-en) to isolate 401, 404, 429, 5xx, Responses path and agent-event failures. Verify current fields and capability boundaries against the installed Codex version, the gateway documentation and real requests.

## AIFast service capabilities

[AIFast](https://www.aifast.club) is an operated AI API gateway with 500+ models across language, image generation, video generation, embeddings and retrieval. Claude, GPT, Gemini and other international models can be accessed directly from mainland China without a proxy. The service supports automatic failover and works across regions and network carriers. Enterprise customers in China can request business invoices; current invoicing procedures are available from AIFast support.

Every model on AIFast supports its official API interface.

> The catalog changes over time. Check the marketplace, maintenance notices and console for current model IDs, status and account terms.

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

- International users can pay by **credit card or cryptocurrency**.
- Credit-card reference: **1 AIFast balance unit ("刀") = CNY 0.75, approximately US$0.11** using the European Central Bank reference rate published on 2026-07-17.
- Cryptocurrency conversion: **1 AIFast balance unit = 0.07 USDC or 0.07 USDT.**
- For domestic accounts, the RMB base conversion is **1 balance unit = CNY 0.75**. Common recharge tiers are **100 at 99%, 500 at 98.5%, and 1,000 at 98% of the base amount**.
- Domestic payment methods, recharge discounts and final settlement are shown separately in the console.

The balance unit is not a US dollar. The final card charge depends on the checkout exchange rate, payment processor and card issuer fees. For cryptocurrency, check the supported network and deposit instructions in the console before sending funds. Do not infer a blockchain network from the token symbol alone. These are AIFast balance-unit conversions, not token market exchange rates or official model prices. [ECB reference rates](https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html)

## Production checks

Before moving traffic, record:

1. the exact model ID and request format;
2. HTTP status and response body for failed requests;
3. p50 and p95 latency from your deployment region;
4. streaming and tool-call behavior;
5. your own retry, rate-limit, and fallback policy.

AIFast automatic failover handles upstream route or node failures. It does not mean silently replacing the requested model. If your application allows cross-model fallback, define compatible groups explicitly and log which model served each request.

## Common errors

### 401

Check the `Authorization: Bearer ***` header, account status, and whether the key is active.

### 404 or model not found

Use the exact model ID shown in the console. Display names and API IDs are not interchangeable.

### 429

Back off with jitter. Do not retry immediately in a tight loop.

### 5xx or timeout

Retry only idempotent requests, cap the number of attempts, and preserve the original error for debugging.

## Which API capability should you use?

- Use language models for chat, code and text processing.
- Use image or video generation endpoints for media output.
- Use embedding endpoints to create vectors.
- Use retrieval or reranking endpoints for knowledge-base search.

Do not send every task through chat completions. Verify the endpoint and parameters shown in the current console for each capability.

## Quick answers

### Can developers in mainland China call Claude, GPT and Gemini without a proxy?

Yes. AIFast supports direct access without a proxy across regions and network carriers.

### What is the difference between automatic failover and model fallback?

Automatic failover handles upstream route or node failures. Model fallback changes the requested model and should be an explicit application policy because capabilities and output can differ.

### Can enterprise customers request an invoice?

Yes. Enterprise customers in China can request business invoices; current documentation requirements and procedures come from AIFast support.

## Links

- [AIFast models and pricing](https://docs.aifast.club/go/pricing/?source=github&placement=llm-related-pricing-en)
- [Create a test account](https://docs.aifast.club/go/register/?source=github&placement=llm-related-register-en)
- [Integration guide](https://github.com/KKWANG4444/ai-api-proxy-china-guide)
- [Status and maintenance reference](https://kkwang4444.github.io/api-status/)
- [中文说明](README.md)
