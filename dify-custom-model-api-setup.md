# Dify 接入第三方 API 模型配置指南

[← 返回主页](README.md)

在 Dify 里用自定义 API provider 接入模型是一个固定的操作流程。这篇文章不说大道理，只写清楚每一步怎么走、字段怎么填、出问题了从哪查。

---

## 1. 配置步骤

### 创建模型供应商

Dify 新版入口是 **Integrations（集成）→ Model Provider（模型供应商）**，也可以从 Marketplace 安装模型供应商插件。只有工作空间 Owner 或 Admin 能管理供应商。

安装支持 OpenAI-compatible 自定义地址的供应商后，再按该插件实际显示的字段填写：

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

Dify 的模型供应商插件必须实现凭据验证，但具体验证端点由插件决定，不能默认认定它只请求 `{base_url}/chat/completions`。保存失败时，先记录界面返回的原始错误，再分别验证 `/models` 和实际业务端点。

**不要一次改多个字段。** 失败时只改一个变量，才能知道是 Key、Base URL、模型 ID，还是供应商插件的协议不兼容。

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

Provider 凭据验证通过，只能说明插件完成了自己的验证流程，不能保证每个模型和能力都可用。实际对话不输出时，依次检查：

1. **模型 ID。** 从 AI快站当前模型目录复制精确 ID，并查看维护公告；配置存在不等于在线。
2. **模型类型。** Dify 把 LLM、Text Embedding、Rerank、Speech2Text、TTS 分成不同接口，不能把对话模型配到 Embedding 类型。
3. **上下文和参数。** 插件声明的上下文长度、最大输出与实际模型能力需要一致。
4. **流式与工具调用。** 普通文本成功后，再分别测试 streaming、tools 和结构化输出。

### 知识库嵌入不工作

Dify 的知识库 RAG 流程分两步：先用 Embedding 模型把文档转成向量，再用 LLM 回答。**嵌入模型和对话模型是独立的。**

需要另外配置一个 Embedding 模型：

- 模型类型选 **Text Embedding**；
- Base URL 仍使用 `https://www.aifast.club/v1`；
- 模型 ID 必须从 AI快站当前模型目录复制。本文不写死第二个候选 ID，避免把已下架或根本不存在的型号留在教程里；
- 配好后用一小段文本生成向量，确认返回数组、维度和 Dify 插件声明一致。

`text-embedding-3-large` 当前存在于公开模型配置，但配置存在不等于在线，生产使用前仍要查看维护公告并发送真实请求。

---

## 4. 多模型配置思路

Dify 的具体配置由已安装的模型供应商插件保存，下面只表示职责分工，不是可以直接导入的 YAML：

```text
对话模型：LLM 类型，用于聊天与工作流
快速模型：LLM 类型，用于分类、摘要等短任务
嵌入模型：Text Embedding 类型，用于知识库向量化
```

三个角色可以共用 `https://www.aifast.club/v1`，但模型类型、精确 ID 和能力参数要分别配置。每项都要在 Dify 中做一次真实调用，不要只看凭据验证结果。

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

- [Dify 官方文档：模型供应商](https://docs.dify.ai/en/cloud/use-dify/workspace/model-providers)
- [AI快站模型与价格](https://docs.aifast.club/go/pricing/)
- [AI快站完整接入指南](https://github.com/KKWANG4444/ai-api-proxy-china-guide)
