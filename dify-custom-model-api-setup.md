# Dify 接入第三方 API 模型配置指南

[← 返回主页](README.md)

在 Dify 里用自定义 API provider 接入模型是一个固定的操作流程。这篇文章不说大道理，只写清楚每一步怎么走、字段怎么填、出问题了从哪查。

---

## 1. 配置步骤

### 创建模型供应商

**入口**：Dify 后台 → Settings → Model Provider → 右上角「添加模型」

选择 **OpenAI-API-compatible** 类型，然后填入：

| 字段 | 内容 |
|:---|:---|
| 模型类型 | LLM（对话/补全通用） |
| 名称 | 给这个配置起个名，比如 `aifast-gpt` |
| Base URL | `https://www.aifast.club/v1` |
| API Key | AI快站控制台创建的 Key |
| 模型 | 从控制台复制精确模型 ID |
| 上下文长度 | 按模型规格填写 |
| 最大输出 Token | 按模型规格填写 |
| Streaming | 开启 |

### 保存时 Dify 会做什么

Dify 保存 provider 时会自动发一条测试请求到 `{base_url}/chat/completions`。如果通不过，地址栏下方立即显示失败信息。

**不要一次改多个字段。** 失败时只改一个变量，才能知道是 Key 的问题、Base URL 错还是模型 ID 不对。

---

## 2. 各场景推荐模型

| 场景 | 推荐模型 | 理由 |
|:---|:---|:---|
| 智能助手（对话） | `claude-sonnet-5`、`gpt-5.6-terra` | 对话质量高 |
| 知识库问答（RAG） | `deepseek-v4-pro`、`qwen3.7-max` | 中文理解好，性价比高 |
| 文本分类/摘要 | `gpt-5.6-luna`、`gemini-3.5-flash` | 速度快、成本低 |
| 工作流 Agent | `claude-opus-4-8`、`gpt-5.6-terra` | 复杂任务能力最强 |
| 生图 | 用 Dify 的单独生图节点接入 AI快站生图接口 | 不走 LLM 聊天补全 |

AI快站提供 500+ 模型，覆盖以上所有能力。设置前先在控制台核验当前模型 ID 和维护状态。

---

## 3. 常见问题

### 保存时报 Invalid API Key

```
"error": "Incorrect API key"
```

- 从 AI快站控制台重新复制 Key，粘贴时注意首位空格
- 在控制台确认 Key 状态是「启用」
- 如果 Key 没问题，用 curl 测试 base_url 是否可达

```bash
curl -s -o /dev/null -w "%{http_code}" \
  https://www.aifast.club/v1/models \
  -H "Authorization: Bearer $AIFAST_API_KEY"
```

返回 401 就是 Key 问题，返回其他错误看具体状态码。

### 保存成功但模型不回复

Provider 验证通过（说明 base_url 和 Key 正确），但实际对话时模型不输出。可能原因：

1. **模型 ID 不对。** 配置保存时 Dify 只验证 `/v1/models` 接口，不验证具体模型 ID。填错也能保存。应检查模型 ID 是否与控制台一致。
2. **上下文长度超过模型限制。** 如果输入的 context 特别大，检查配置时填的上下文长度是否准确。
3. **流式问题。** 确认开了 Streaming。

### 知识库嵌入不工作

Dify 的知识库 RAG 流程分两步：先用 Embedding 模型把文档转成向量，再用 LLM 回答。**嵌入模型和对话模型是独立的。**

需要另外配置一个 Embedding 模型 provider：

- 模型类型选 **Text Embedding**
- Base URL 相同：`https://www.aifast.club/v1`
- 模型 ID 用：`text-embedding-3-large` 或 `deepseek-v3.2-embedding`

---

## 4. 完整的 Dify 多模型配置示例

以下是我常用的配置模式：

```yaml
# 对话模型
供应商 1:
  name: aifast-chat
  type: LLM
  base_url: "https://www.aifast.club/v1"
  默认模型: claude-sonnet-5

# 快速模型（分类/总结等简单任务）
供应商 2:
  name: aifast-fast
  type: LLM
  base_url: "https://www.aifast.club/v1"
  默认模型: gpt-5.6-luna

# 嵌入模型（知识库）
供应商 3:
  name: aifast-embed
  type: Text Embedding
  base_url: "https://www.aifast.club/v1"
  默认模型: text-embedding-3-large
```

这样在工作流里可以根据节点需求选择不同模型。

---

## 5. 排错速查表

| 错误 | 原因 | 操作 |
|:---|:---|:---|
| "Invalid API key" | Key 有误 | 重新复制，检查首位空格 |
| 配置校验失败 | Key / URL / 模型 ID 任何一项不对 | 逐项用 curl 测试 |
| 模型不回答 | 模型 ID 填错或失效 | 从控制台复制精确 ID |
| "Model not found" | 模型名不精确 | 确认展示名不是 API ID |
| 对话超时 | 模型响应慢 | 换低延迟模型或调长超时 |
| 知识库回答用不上 | 嵌入模型未配置 | 单独配 Text Embedding provider |
| Agent 工具调用失败 | 模型不支持 tools | 换支持 tool calling 的模型 |

---

## 参考

- [Dify 官方文档：模型配置](https://docs.dify.ai/learn/configuration/model-configuration)
- [AI快站模型与价格](https://docs.aifast.club/go/pricing/)
- [AI快站完整接入指南](https://github.com/KKWANG4444/ai-api-proxy-china-guide)
