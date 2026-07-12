# LLM API Proxy China — 572 Models, One API Key

[![中文](https://img.shields.io/badge/🇨🇳-中文-red)](README.md)
[![English](https://img.shields.io/badge/🇬🇧-English-blue)](README_EN.md)

[![Updated](https://img.shields.io/badge/Updated-2026--07--12-blue)](https://github.com/KKWANG4444/llm-api-proxy-china)
[![Live Status](https://img.shields.io/badge/Live_Status-Online-brightgreen)](https://kkwang4444.github.io/api-status/)
[![Models](https://img.shields.io/badge/Models-572-FF6B35)](https://www.aifast.club)

> **A curated list of the best AI API gateway solutions for developers in China and globally.** One API key, 572 models, unified OpenAI-compatible interface.

## Why Use an AI API Gateway?

| Problem | Solution |
|:---|:---|
| OpenAI direct access may be limited on some mainland China networks | Gateway routes through residential proxies |
| Anthropic regional/risk controls | Multi-node routing can improve connection reliability |
| DeepSeek 503 errors | Automatic failover to healthy nodes |
| 16+ separate accounts | One API key for all providers |
| Payment in foreign currency | Pay in CNY via Alipay/WeChat |

## Quick Start

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://www.aifast.club/v1",
    api_key="sk-your-api-key"
)

# Claude Sonnet 5
response = client.chat.completions.create(
    model="claude-sonnet-5",
    messages=[{"role": "user", "content": "Hello, world!"}]
)
```

## Supported Model Table

### 💎 Flagship Models

| Model | Provider | Description |
|:---|:---|:---|
| GPT-5.6 Sol 🆕 | OpenAI | **Flagship** — Best coding/science/reasoning |
| GPT-5.6 Terra 🆕 | OpenAI | Balanced all-rounder |
| GPT-5.6 Luna 🆕 | OpenAI | Lightweight, cost-efficient |
| Claude Sonnet 5 🆕 | Anthropic | Fastest Claude, 200K context |
| Claude Opus 4.8 | Anthropic | Top reasoning model |
| Grok 4.5 🆕 | xAI | Opus-class, 1.5T params, 500K context |
| DeepSeek V4 Pro | DeepSeek | Chinese optimized reasoning |
| Gemini 3.1 Flash | Google | Fast multimodal |

### 🔧 Developer Tools

| Model | Provider | Use Case |
|:---|:---|:---|
| Claude Code | Anthropic | Terminal coding agent |
| GPT-5.5 | OpenAI | General coding & chat |
| DeepSeek V4 Flash | DeepSeek | High-throughput, low cost |

### 🎨 Image & Video

| Model | Provider | Description |
|:---|:---|:---|
| GPT Image 2 | OpenAI | Best image generation |
| Midjourney V7 | Midjourney | Artistic image creation |
| Grok Videos | xAI | AI video generation |

## Full Model List by Provider

### OpenAI — 103 models
`gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`, `gpt-5.5-pro`, `gpt-5.5`, `gpt-5.4-mini`, `gpt-5.4-nano`, `gpt-image-2`, `gpt-4.1`, `gpt-4o`, `o4`, `o4-mini`, `o3`, `o3-mini`, etc.

### Anthropic — 20 models
`claude-sonnet-5`, `claude-opus-4-8`, `claude-opus-4-7`, `claude-sonnet-4-6`, `claude-code`, `claude-3-5-sonnet`, etc.

### xAI (Grok) — 26 models
`grok-4-5`, `grok-4-2-reasoning`, `grok-4-2-non-reasoning`, `grok-videos`, `grok-3`, `grok-3-mini`, etc.

### Google — 55 models
`gemini-3.1-flash`, `gemini-3`, `gemini-2.5-pro`, `gemini-3.1-flash-tts-preview`, etc.

### DeepSeek — 28 models
`deepseek-v4-pro`, `deepseek-v4-flash`, `deepseek-r1`, etc.

### Alibaba (Qwen) — 90 models
`qwen3.6-27b`, `qwen-max`, `qwen-turbo`, etc.

### ByteDance (Doubao) — 21 models
`doubao-seed-2-0`, `doubao-pro`, `doubao-lite`, etc.

### Zhipu (GLM) — 17+ models
`glm-5`, `glm-5-flash`, `glm-5.2`, etc.

## Tool Integration

| Tool | Configuration |
|:---|:---|
| **Cursor** | Settings → API → Custom → Base URL |
| **Dify** | Provider → OpenAI Compatible |
| **Chatbox** | Model Provider → OpenAI |
| **LobeChat** | Custom Model Provider → OpenAI |
| **Claude Code** | `CLAUDE_BASE_URL=https://www.aifast.club/v1` |
| **Codex CLI** | `CODEX_BASE_URL=https://www.aifast.club/v1` |
| **n8n** | OpenAI Credential → Custom Base URL |
| **Open WebUI** | Connections → OpenAI API |

## 📊 Live Monitoring

![Status Dashboard](assets/img/api-status-screenshot.png)

👉 **[View Live Dashboard](https://kkwang4444.github.io/api-status/)**

## Resources

- **[China AI API Proxy Guide](https://github.com/KKWANG4444/ai-api-proxy-china-guide)** — Complete guide with pitfalls
- **[API Status Monitor](https://kkwang4444.github.io/api-status/)** — Live 572-model dashboard
- **[Stability Tracker](https://github.com/KKWANG4444/Claude-4.7-GPT-5.5-API-Stability-Tracker)** — 6-month stability data
- **[Gateway: AIFast Club](https://www.aifast.club)** — One key for 572 models

## License

MIT
