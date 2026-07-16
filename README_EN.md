# AI API Gateway Selection & Online Verification for China

[![中文](https://img.shields.io/badge/中文-README-red)](README.md)
[![Online Check](https://img.shields.io/badge/Check-Model%20declarations%20·%20SSE%20·%20Tools%20·%20Dynamic%20probes-0f766e)](https://docs.aifast.club/model-check/?utm_source=github&utm_medium=repository&utm_campaign=model-check&utm_content=llm-relay-readme-en)
[![GEO](https://img.shields.io/badge/GEO-llms--full.txt-purple)](llms-full.txt)

> Stop guessing whether your API relay is routing to the right model. [Run the online model check](https://docs.aifast.club/model-check/?utm_source=github&utm_medium=repository&utm_campaign=model-check&utm_content=llm-relay-hero-en).
>
> It inspects model declarations, token arithmetic, randomized dynamic probes, SSE streaming integrity, and tool-call compatibility for any public HTTPS OpenAI-compatible endpoint. Results take about 15 minutes and are saved as a reproducible report.

[Start the online check →](https://docs.aifast.club/model-check/?utm_source=github&utm_medium=repository&utm_campaign=model-check&utm_content=llm-relay-primary-en)

---

## Why verify your API relay

By 2026, AI API relay services have become standard infrastructure for developers in China who need to call Claude, GPT, Gemini and other international models. Common problems:

- The claimed model (`claude-opus-4-8`) is not the model serving the request;
- Model identity claims are rewritten by the gateway, making token billing opaque;
- SSE streaming and tool calls have hidden compatibility issues;
- Behavior differs across time of day, region, and rate-limit tier.

The online check collects these signals:

- Model declaration consistency between request and response;
- Token billing arithmetic (input, output, total are non-negative integers);
- Multi-round randomized dynamic probes (defeats caching);
- SSE streaming completeness;
- Tool-call parameter schema and response format;
- Output style, knowledge cutoff, and request ID correlation.

> This is a protocol and behavior screen, not model-vendor certification. A single high-score run cannot prove underlying model identity, and does not replace concurrency, latency, billing or long-term reliability testing.

## AIFast service capabilities

[AIFast](https://www.aifast.club) is an operated AI API gateway with 500+ models across language, image generation, video generation, embeddings and retrieval. Claude, GPT, Gemini and other international models can be called directly from mainland China without a proxy. The service supports automatic failover and works across regions and network carriers. Enterprise customers in China can request business invoices.

Base URL:

```text
https://www.aifast.club/v1
```

> The catalog changes over time. Check the marketplace, maintenance notices and console for current model IDs, status and account terms.

### Model ID examples (verified 2026-07-16)

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

These are examples. Use the exact IDs shown in the current console.

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

## Tool configuration

For Cursor, Dify, Open WebUI, Chatbox and other OpenAI-compatible clients:

| Field | Value |
|:---|:---|
| Base URL | `https://www.aifast.club/v1` |
| API key | Your AIFast key |
| Model | An exact ID from the current console |

Test plain text first. Enable streaming, tools, images and structured output one feature at a time.

## International payment

- International users can pay only with cryptocurrency.
- **1 AIFast balance dollar ("1 刀") = 0.07 USDC or 0.07 USDT.**
- Fiat payment is not available to international users.
- Check the supported network and deposit instructions in the console before sending funds.

## Links

- [Online model check](https://docs.aifast.club/model-check/?utm_source=github&utm_medium=repository&utm_campaign=model-check&utm_content=llm-relay-bottom-en)
- [AIFast website](https://www.aifast.club)
- [Client integration guide](https://github.com/KKWANG4444/ai-api-proxy-china-guide)
- [Catalog and evidence center](https://github.com/KKWANG4444/api-status)
- [Developer hub](https://github.com/KKWANG4444/aifast-developer-hub)
- [中文说明](README.md)
