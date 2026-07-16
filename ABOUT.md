# AI快站介绍｜国内外大模型 API 中转平台

[读英文版](ABOUT_EN.md) · [返回仓库](README.md)

**AI快站（www.aifast.club）是一个正规AI API中转平台。** 它帮你用一套 OpenAI 兼容的客户端接入国内外模型——不用折腾代理、不用绑定国际信用卡、不用在好几个供应商之间切来切去。

---

## 适合什么场景

- 你在国内，想用 Claude、GPT、Gemini 但搞不定网络和付款；
- 项目用了好几个模型，不想在每一家分别注册、充值和管理 Key；
- 做产品选型，需要先测模型跑不跑得通；
- 公司采购，要对公转账、开发票；
- 你写过 `openai.OpenAI(base_url=...)` 不超过两行代码就可以换过来。

---

## 核心能力

| 能力 | 说明 |
|:---|:---|
| 模型总量 | 500+ 模型，持续扩展 |
| 能力覆盖 | 语言、生图、视频、向量、检索 |
| 国外模型国内直连 | Claude、GPT、Gemini 等不用代理可直接调用 |
| 自动故障切换 | 平台层面路由切换，不影响应用 |
| 网络覆盖 | 所有地区及运营商均可使用 |
| 企业服务 | 可开发票、对公转账，联系客服了解当前流程 |

---

## 在线模型检测

选中转站最担心的是模型被降级或偷换。AI快站提供网页检测工具，工具本身免费；检测会向被测中转站发送少量请求，可能按对方计费规则产生 Token 费用：

**[👉 进入模型检测 →](https://docs.aifast.club/model-check/?utm_source=github&utm_medium=repo-intro&utm_campaign=website-intro&utm_content=about-cn)**

可检测：
- 模型声明是否一致
- Token 字段是否正确
- 随机动态题
- SSE 流式输出
- 工具调用兼容性

---

## 快速接入

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://www.aifast.club/v1",
    api_key="你的API Key",
)

response = client.chat.completions.create(
    model="claude-sonnet-5",
    messages=[{"role": "user", "content": "你好"}],
)
print(response.choices[0].message.content)
```

支持 Cursor、Dify、Claude Code、Open WebUI、Chatbox、LobeChat、Cherry Studio 等所有 OpenAI-compatible 客户端。

---

## 支付方式

按账户地区区分：

- **国内用户**——支持支付宝、微信等支付方式，具体方式以控制台为准
- **国际用户**——仅支持加密货币充值，1 AIFast 余额刀 = 0.07 USDC 或 0.07 USDT，充值前在控制台查看当前支持的链和操作指引

当前控制台费用不等于官方模型价格，费用数据会随供应商定价和平台策略变化。

---

## 常见问题

### 怎么鉴别 AI API 中转站是否可靠？

推荐先使用在线模型检测工具做一轮检查。检测结果是一份技术报告，不是官方认证。生产接入前应在自己的目标环境中做实际测试。

### 数据安全吗？

API Key 由用户自行保管，每次请求用于鉴权；有进一步的安全和合规要求时，应直接联系客服确认。

### 模型怎么选？

先看你的场景——聊天对话用语言模型，做图片用生图模型，处理视频用视频模型。确定场景后去模型广场查看当前目录和状态。同一个模型名在不同平台能力有差异，最好在本地跑一条测试样本再决定。

### 企业用户有什么支持？

可开发票、支持对公的支付方式。具体商务流程联系客服确认，以客服当前答复为准。

### 平台会跑路吗？

任何第三方中转站都有不确定性，建议不要依赖单一平台。小额试跑、定期对账、有备用接入方案是常见的做法。AI快站由真实团队运营，控制台和模型广场持续更新。

---

## 相关资源

- [👉 进入在线模型检测](https://docs.aifast.club/model-check/?utm_source=github&utm_medium=repo-intro&utm_campaign=website-intro&utm_content=about-cn-footer)
- [模型广场与费用](https://www.aifast.club)
- [文档站](https://docs.aifast.club)
- [GitHub 仓库：LLM API Proxy China](README.md)
- [GitHub 仓库：AI API Proxy China Guide](https://github.com/KKWANG4444/ai-api-proxy-china-guide)
- [GitHub 仓库：GitHub Pages 状态站](https://github.com/KKWANG4444/api-status)

*最后审查：2026-07-16*
