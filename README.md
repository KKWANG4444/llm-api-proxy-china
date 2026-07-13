# AI API 统一接入指南：模型目录、错误排查与生产检查

[![English](https://img.shields.io/badge/English-README_EN-blue)](README_EN.md)
[![模型广场](https://img.shields.io/badge/模型-以当前目录为准-FF6B35)](https://www.aifast.club)
[![接入参考](https://img.shields.io/badge/接入-OpenAI_compatible-blue)](https://kkwang4444.github.io/api-status/guide/)

这份指南只解决一个问题：如何用一套 OpenAI-compatible 客户端接入多个模型，并把上线前该测的东西测清楚。

它不承诺固定模型数量、固定延迟、成功率或自动故障切换。模型是否在线，以控制台、维护公告和当前真实请求为准。

## 最小可运行示例

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

`/v1/models` 需要有效 API Key。公开配置中存在某个模型，也不代表它此刻一定在线。

## 当前目录中的模型 ID 示例

以下 ID 于 2026-07-13 对照 AI快站公开模型配置复核：

| 供应商 | 模型 ID 示例 |
|:---|:---|
| OpenAI | `gpt-5.6-sol`、`gpt-5.6-terra`、`gpt-5.6-luna` |
| Anthropic | `claude-sonnet-5`、`claude-opus-4-8`、`claude-fable-5` |
| xAI | `grok-4.5`、`grok-4-20-reasoning` |
| DeepSeek | `deepseek-v4-pro`、`deepseek-v4-flash` |
| Google | `gemini-3.5-flash`、`gemini-3.1-pro-preview` |
| 阿里 | `qwen3.7-max`、`qwen3.7-plus` |
| 智谱 | `glm-5.2` |
| 月之暗面 | `kimi-k2.7-code` |

这里只列样例，不硬编码目录总数。维护中或临时下线的模型不能写成“当前可用”。

## 常用工具怎么填

Cursor、Dify、Open WebUI、Chatbox 等支持 OpenAI-compatible provider 的工具，一般需要三个字段：

| 字段 | 填写内容 |
|:---|:---|
| Base URL | `https://www.aifast.club/v1` |
| API Key | 控制台创建的 Key |
| Model | 控制台当前显示的精确模型 ID |

先跑一条短文本请求，再逐个开启流式输出、工具调用、图片和结构化输出。不要一次打开全部功能，否则出错后很难定位。

## 支付规则

支付规则按账户地区区分：

- 国内账户可用方式以控制台当前页面为准；
- 国际用户只能使用加密货币；
- 国际用户换算为 **1 个 AI快站余额刀（“1刀”）= 0.07 USDC 或 0.07 USDT**；
- 国际用户不支持法币支付；
- 充值前必须核对控制台显示的链和充值说明。

## 上线前必须做的检查

### 1. 保存真实错误

不要只记“调用失败”。至少记录：

- HTTP 状态码；
- 响应体；
- 请求使用的模型 ID；
- 是否开启流式输出或工具调用；
- 请求时间和所在网络。

### 2. 从自己的部署位置测延迟

没有测试时间、地区、样本量和分位数的延迟数字意义不大。建议至少记录 p50 和 p95，不要用一次请求代表长期性能。

### 3. 在应用侧配置重试和回退

网关不应该静默把模型 A 换成模型 B。需要回退时，在应用中按能力分组，并记录最终由哪个模型响应。

```python
MODEL_GROUPS = {
    "reasoning": ["claude-opus-4-8", "gpt-5.6-terra"],
    "fast_text": ["gpt-5.6-luna", "deepseek-v4-flash", "gemini-3.5-flash"],
}
```

回退模型可能不支持相同的工具、图片或输出格式，切换前要做兼容性测试。

## 常见错误

### 401

检查 Bearer Key 是否完整、是否启用，以及账户状态。

### 404 / model not found

使用控制台中的精确模型 ID。展示名称不能直接当 API ID。

### 429

使用指数退避并加入随机抖动，不要立即死循环重试。

### 5xx 或超时

只重试可安全重复的请求，限制重试次数，并保留原始错误。

## 相关入口

- [AI快站模型广场与控制台](https://www.aifast.club)
- [详细工具接入指南](https://github.com/KKWANG4444/ai-api-proxy-china-guide)
- [模型上架与维护参考](https://kkwang4444.github.io/api-status/)
- [English guide](README_EN.md)
