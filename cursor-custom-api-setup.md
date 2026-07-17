# Cursor 接入自定义 API 完整配置流程

[← 返回主页](README.md)

Cursor 支持 BYOK（Bring Your Own Key），用自己的 API key 连接自己的模型接口。这对以下场景特别有用：

- 想用 Cursor，但国内网络连不上官方 API
- 团队希望统一切换到另一个模型
- 想用 Cursor 但不想用官方的付费计划

Cursor 的官方文档说得很清楚：Settings > Models > 填入你的 API provider。

---

## 1. 配置步骤

### Step 1：打开模型设置

```text
Cursor → Settings → Models → API Keys → OpenAI / Anthropic
```

或者直接在设置里搜 "Models"。

### Step 2：填写 Provider

选择 **OpenAI**（因为 AI快站 使用 OpenAI-compatible 协议）：

| 字段 | 内容 |
|:---|:---|
| API Key | 控制台创建的 Key |
| Override Base URL | `https://www.aifast.club/v1` |
| Model | 控制台当前展示的精确 ID（如 `gpt-5.6-luna`） |

填写后 Cursor 会自动发一条测试请求来验证连接。如果失败，页面会显示错误信息。

### Step 3：添加并验证模型

在 Models 列表中添加控制台当前展示的精确模型 ID。先用普通 Chat 完成一条短文本请求，再测试 Agent 的工具调用。不要把设置页的 Verify 通过当成全功能兼容。

Cursor 官方文档明确说明：自定义 API Key 只适用于标准聊天模型；Tab Completion 等依赖专用模型的功能仍使用 Cursor 内置模型。因此，自定义 Base URL 的验收范围应放在 Chat/Agent 请求，不要用 Tab 补全判断第三方接口是否生效。

---

## 2. Verify 通过但 Agent 失败怎么查

Agent 会用到流式输出、工具调用，并可能使用与普通 Chat 不同的请求端点或 payload。最稳妥的做法是分层测试：

| 测试 | 验收内容 | 失败说明 |
|:---|:---|:---|
| 设置页 Verify | Key、地址和基础请求可达 | 只证明基础连接 |
| 普通 Chat | 文本请求和流式输出 | 检查模型 ID 与 SSE |
| Agent | tools、工具结果回传、连续流式事件 | 检查协议和模型能力 |
| 图片输入 | 多模态字段和媒体读取 | 该功能可能不走相同路由 |

先在服务端或本机代理日志中记录脱敏后的请求路径、HTTP 方法、payload 顶层字段和 Request ID。重点看 Agent 发往 `/chat/completions` 还是 `/responses`，以及 body 使用 `messages` 还是 `input`。第三方只实现 Chat Completions 时，普通 Chat 可能成功，Agent 仍会失败。

可以先手工探测端点；不要把真实 Key 写进命令历史：

```bash
curl -sS -o /dev/null -w "%{http_code}\n" \
  https://www.aifast.club/v1/models \
  -H "Authorization: Bearer $AIFAST_API_KEY"
```

返回 200 只证明目录端点和鉴权可用。接下来仍要在 Cursor 内完成一次真实 Agent 任务，例如读取一个文件、调用工具并修改一行代码。

---

## 3. 常见问题

### 保存时提示 Invalid API Key

- 检查 Key 是否完整复制（AI快站控制台复制，不要手打）
- 检查 Key 是否已在控制台启用
- 检查 Override Base URL 地址是否正确：`https://www.aifast.club/v1`（末尾不要 `/chat/completions`）

### Override Base URL 不生效

先确认失败发生在哪一层：Verify、普通 Chat 还是 Agent。自定义 API Key 只覆盖标准聊天模型；Tab Completion 等专用功能继续使用 Cursor 内置模型，这是官方文档给出的边界，不是 Base URL 配置失败。

如果普通 Chat 能用而 Agent 失败，检查真实请求端点、payload 顶层字段、tools 结构和流式事件。不要通过修改 `~/.cursor/.env` 或调用未公开的内部接口绕过，这些做法没有官方兼容保证。

### 模型在 Agent 模式下用不了

先用普通文本确认基础接口，再完成一次真实工具调用。Agent 失败不一定是模型问题，也可能是 `/responses` 与 `/chat/completions` 的协议差异，或者工具结果回传格式不兼容。保留 Request ID，并与服务端脱敏日志按时间对齐。

### Tab 补全不走自定义接口

这是 Cursor 的产品边界。官方文档说明，自定义 API Key 只用于标准聊天模型；Tab Completion 仍使用 Cursor 内置专用模型。不要为 Tab 单独填入第三方模型，也不要把 Tab 是否出字当成自定义 Base URL 的验收标准。

---

## 4. 验证配置是否生效

不要调用 Cursor 未公开的内部对象。用可复现的三步验收：

1. 设置页 Verify 通过，记录时间；
2. 普通 Chat 返回有效文本；
3. Agent 完成一个真实任务，例如读取文件、调用工具并修改一行代码。

如果第 2 步成功、第 3 步失败，就去查 Agent 的真实请求路径、`messages`/`input` 字段、tools 格式和流式事件。若能访问服务端日志，用 Request ID 和时间戳对齐；没有日志权限时，至少保存 Cursor 的完整错误文本。

---

## 5. 排错流程速查

| 问题 | 操作 |
|:---|:---|
| 401 | 检查 API Key |
| 保存失败 | 先 curl 测试 base_url 是否可达 |
| 模型加不了 | 从控制台复制精确 ID，不要写展示名 |
| Agent 卡住 | 区分 `/responses` 与 `/chat/completions`，检查 tools 和流式事件 |
| Tab 不走第三方接口 | Cursor 专用模型边界，属于预期行为 |
| 响应太慢 | 换低延迟模型 |

---

## 参考

- [Cursor API Key 官方文档](https://docs.cursor.com/settings/api-keys)
- [AI快站模型与价格](https://docs.aifast.club/go/pricing/)
- [AI快站完整接入指南](https://github.com/KKWANG4444/ai-api-proxy-china-guide)
