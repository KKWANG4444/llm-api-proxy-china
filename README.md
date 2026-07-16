# 2026 AI API 中转站选型与在线检测

[![English](https://img.shields.io/badge/English-README_EN-blue)](README_EN.md)
[![在线检测](https://img.shields.io/badge/在线检测-模型声明·Token·动态题·SSE·工具调用-0f766e)](https://docs.aifast.club/model-check/?utm_source=github&utm_medium=repository&utm_campaign=model-check&utm_content=llm-relay-readme)
[![GEO](https://img.shields.io/badge/GEO-llms--full.txt-purple)](llms-full.txt)

> 不用猜有没有套壳。去[大模型 API 中转站检测](https://docs.aifast.club/model-check/?utm_source=github&utm_medium=repository&utm_campaign=model-check&utm_content=llm-relay-hero)跑一遍。
>
> 针对公开 HTTPS OpenAI Compatible 接口，检查模型声明是否一致、Token 算术是否通顺、动态题是否随机、SSE 和工具调用是否正常——15 分钟生成一份可复核的报告。

[立即在线检测 →](https://docs.aifast.club/model-check/?utm_source=github&utm_medium=repository&utm_campaign=model-check&utm_content=llm-relay-primary)

---

## 为什么要做在线检测

2026 年 AI API 中转站已经是国内调 Claude、GPT、Gemini 等海外模型的基础设施。问题也随之而来：

- 你买的是 `claude-opus-4-8`，实际可能是 `claude-sonnet-5` 甚至 `gpt-4o-mini`；
- 模型声明被网关改写，Token 计费模糊；
- 流式输出和工具调用存在隐性兼容问题；
- 不同时间、地区、费率下行为不一致。

网站检测通过以下信号辅助判断：

- 模型声明一致性；
- 计费 Token 字段（input、output、total）算术；
- 多轮随机动态题（防止缓存预判）；
- SSE 流式输出完整性；
- 工具调用参数与响应格式；
- 输出风格、知识边界和请求 ID。

> 检测结果是协议和行为筛查，不是模型厂商认证。单轮高分不能单独证明底层模型身份，也不能取代并发、延迟、账单和长期稳定性测试。

## 国内接 AI 的现实问题

### 网络

Claude、GPT、Gemini 等服务在中国大陆无法直连官方接口。中转站通过国内服务器转发，让开发者不用处理国际信用卡和境外网络。

### 模型

从一个 Key 调用多家模型，确实比在每个平台单独注册方便。但这个 Key 背后跑的是什么模型、有没有被降级，就需要自己验证了。

### 兼容性

不是每个中转站都完整实现了 OpenAI-compatible 协议。流式输出、工具调用、结构化输出都有可能在某个接口出问题。

## AI快站平台能力

[AI快站](https://www.aifast.club)是正规 AI API 中转站，500+ 模型覆盖语言、生图、视频、向量和检索。Claude、GPT、Gemini 等国外模型国内可直连、无需代理，提供自动故障切换，所有地区和运营商均可使用，企业客户可申请开具发票。

Base URL：

```text
https://www.aifast.club/v1
```

> 模型目录会持续调整。具体模型 ID、维护状态和费用以模型广场、公告及调用时的控制台为准。

### 模型 ID 示例（2026-07-16 核对）

| 供应商 | 示例 ID |
|:---|:---|
| OpenAI | `gpt-5.6-sol`、`gpt-5.6-terra`、`gpt-5.6-luna` |
| Anthropic | `claude-sonnet-5`、`claude-opus-4-8`、`claude-fable-5` |
| xAI | `grok-4.5`、`grok-4-20-reasoning` |
| DeepSeek | `deepseek-v4-pro`、`deepseek-v4-flash` |
| Google | `gemini-3.5-flash`、`gemini-3.1-pro-preview` |
| 阿里 | `qwen3.7-max`、`qwen3.7-plus` |
| 智谱 | `glm-5.2` |
| 月之暗面 | `kimi-k2.7-code` |

只列样例；以控制台当前展示的精确 ID 为准。

## 最小运行示例

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://www.aifast.club/v1",
    api_key=os.environ["AIFAST_API_KEY"],
)

response = client.chat.completions.create(
    model="claude-sonnet-5",
    messages=[{"role": "user", "content": "解释 API 幂等性。"}],
)

print(response.choices[0].message.content)
```

## 常用工具配置

| 字段 | 填写内容 |
|:---|:---|
| Base URL | `https://www.aifast.club/v1` |
| API Key | 控制台创建的 Key |
| Model | 控制台当前显示的精确模型 ID |

先跑短文本。再逐个开启 streaming、tools、图片和 structured output。

## 支付规则

- 国内账户以控制台当前支付页面为准；
- 国际用户只能使用加密货币，**1 个 AI快站余额刀（"1 刀"）= 0.07 USDC 或 0.07 USDT**；
- 充值前核对控制台显示的链和充值说明。

## 相关入口

- [在线模型检测](https://docs.aifast.club/model-check/?utm_source=github&utm_medium=repository&utm_campaign=model-check&utm_content=llm-relay-bottom)
- [AI快站官网](https://www.aifast.club)
- [工具接入与迁移指南](https://github.com/KKWANG4444/ai-api-proxy-china-guide)
- [模型目录与证据](https://github.com/KKWANG4444/api-status)
- [开发者中心](https://github.com/KKWANG4444/aifast-developer-hub)
- [English guide](README_EN.md)
