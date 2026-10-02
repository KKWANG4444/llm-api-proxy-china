# Cursor 自定义 API 配置：Base URL、Agent 与 Cursor2API 区别

[← 返回主页](README.md)

> **先判断问题在哪一层：** [运行网页模型质量检测](https://docs.aifast.hk/model-check/?utm_source=github&utm_medium=repository&utm_campaign=model-check&utm_content=cursor-setup-hero-model-check)检查鉴权、模型声明、Token、SSE 和工具调用；需要核对 Cursor 新旧版本入口、Verify 按钮和功能边界时，继续阅读[新版 Cursor 配置教程](https://docs.aifast.hk/tools/cursor/?utm_source=github&utm_medium=repository&utm_campaign=integration-guide&utm_content=cursor-setup-hero-docs)。无需下载检测程序。

> **先区分两条链路：** Cursor 官方自定义 API Key 是 Cursor 当前版本提供的 BYOK 能力；Cursor2API 是社区协议转换项目，两者不是同一功能。如果你使用的是 Cursor2API，请先看 [Cursor2API 配置、401、截断与迁移指南](https://docs.aifast.hk/tools/cursor2api/?utm_source=github&utm_medium=repository&utm_campaign=api-doctor&utm_content=cursor-setup-cursor2api)。

Cursor 支持 BYOK（Bring Your Own Key），可用自己的 API Key 连接受支持的模型接口。设置入口和能力范围会随 Cursor 版本、套餐与提供商变化，配置前应先核对当前官方说明。这对以下场景特别有用：

- 想用 Cursor，但国内网络连不上官方 API
- 团队希望统一切换到另一个模型
- 希望由所选模型提供商单独计费，并保留当前 Cursor 套餐的功能边界

自带 Key 不自动替代 Cursor 订阅或解锁全部功能。模型服务商仍会收取调用费用，团队或企业套餐还可能涉及 Cursor 的用量费用；请核对当前套餐规则。

Cursor 官方的自带 Key 设置入口是 Settings > Models。2026-10-02 核对时，官方把 OpenAI 自带 Key 的范围限定为标准、非推理聊天模型，实际可选项以模型选择器为准；中转站目录中的全部 GPT 模型不能自动视为 Cursor 支持列表。

## 先按现象定位

| 你遇到的问题 | 直接查看 |
|:---|:---|
| 找不到 Override OpenAI Base URL | [检查版本和提供商入口](#找不到-override-openai-base-url) |
| API Key Valid，但实际聊天失败 | [核对模型选择器、请求路径与日志](#api-key-valid但聊天失败) |
| 本机 curl 正常，Cursor 连不上 | [区分本机与 Cursor 服务器链路](#本机-curl-成功cursor-还是连不上) |
| Chat 能用，Agent 卡住 | [逐层验证流式和工具调用](#2-verify-通过但-agent-失败怎么查) |

第三方接口示例只适用于当前 Cursor 版本提供自定义 Base URL 的情况；官方支持自带 Key，不等于保证任意第三方网关兼容。

---

## 1. 配置步骤

### Step 1：打开模型设置

```text
Cursor → Settings → Models → API Keys → OpenAI / Anthropic
```

或者直接在设置里搜 "Models"。

### Step 2：填写 Provider

若当前版本提供 OpenAI 的自定义 Base URL，按以下字段配置 AI快站的 OpenAI-compatible 接口；不要把中转 Key 填入仍指向模型厂商的地址：

| 字段 | 内容 |
|:---|:---|
| API Key | 控制台创建的 Key |
| Override Base URL | `https://www.aifast.hk/v1` |
| Model | 从控制台当前模型目录复制的精确模型 ID，不要填写展示名或自行猜测别名 |

填写后按当前版本的 Save 或 Verify 操作保存、验证，再发起一条短请求。如果失败，保留完整错误信息，不把按钮名称或旧版界面当成固定步骤。

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
  https://www.aifast.hk/v1/models \
  -H "Authorization: Bearer $AIFAST_API_KEY"
```

返回 200 只证明目录端点和鉴权可用。接下来仍要在 Cursor 内完成一次真实 Agent 任务，例如读取一个文件、调用工具并修改一行代码。

---

## 3. 常见问题

### 找不到 Override OpenAI Base URL

先核对当前 Cursor 版本和提供商设置。官方自带 Key 文档列出提供商 Key 的填写步骤，没有保证每个版本都提供第三方 Base URL 入口。没有该选项时，不要通过修改未公开配置强行开启，也不要假定保存第三方 Key 后地址会自动切换。

先用 [Base URL 检查器](https://docs.aifast.hk/tools/base-url-checker/?utm_source=github&utm_medium=repository&utm_campaign=api-doctor&utm_content=cursor-missing-base-url)检查地址，再按 [OpenAI-compatible 接入教程](https://docs.aifast.hk/guides/openai-compatible-api/?utm_source=github&utm_medium=repository&utm_campaign=integration-guide&utm_content=cursor-fallback-sdk)验证本机接口。两者成功也不代表当前 Cursor 支持该端点。

### API Key Valid，但聊天失败

1. 记录聊天模型选择器中的模型 ID，确认它与设置页验证的模型一致；不要把平台目录当作客户端支持列表。
2. 新开聊天，只发一条短文本，暂不附加文件、图片或工具。
3. 按时间、模型 ID 和请求 ID 核对服务商日志。没有请求记录时，先排查客户端配置和 Cursor 服务器到接口的链路。
4. 有请求记录时，按实际状态码、端点和响应正文处理；返回 HTML 首页不能算有效 JSON API 响应。

没有日志权限时，保存客户端版本、完整错误文本和发生时间，分享前删除 API Key、认证头和私有代码。

### 本机 curl 成功，Cursor 还是连不上

Cursor 官方说明，自带 API Key 的请求仍经过 Cursor 服务器进行最终提示词构建。本机测试成功不能证明 Cursor 服务器到目标接口也可达，`localhost` 也不代表你的电脑对 Cursor 服务器可见。记录失败时间、状态码和模型 ID，再与服务商的调用日志核对；没有日志权限时保留完整报错。

Cursor 的零数据保留政策不自动适用于自带 Key 的请求，私有代码处理应同时核对 Cursor 与所选模型提供商的当前政策。

### 保存时提示 Invalid API Key

- 检查 Key 是否完整复制（AI快站控制台复制，不要手打）
- 检查 Key 是否已在控制台启用
- 检查 Override Base URL 地址是否正确：`https://www.aifast.hk/v1`（末尾不要 `/chat/completions`）

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
| 401 | [检查 Key、鉴权头与账号状态](https://docs.aifast.hk/troubleshooting/401-invalid-api-key/?utm_source=github&utm_medium=repository&utm_campaign=api-doctor&utm_content=cursor-setup-table-401) |
| 保存失败 | 先测试本机链路，再核对 Cursor 报错与服务商日志 |
| 模型加不了 | 从控制台复制精确 ID，不要写展示名 |
| Agent 卡住 | 区分 `/responses` 与 `/chat/completions`，检查 tools 和流式事件 |
| Tab 不走第三方接口 | Cursor 专用模型边界，属于预期行为 |
| 429、额度或并发限制 | [区分限流与额度问题](https://docs.aifast.hk/troubleshooting/429-rate-limit/?utm_source=github&utm_medium=repository&utm_campaign=api-doctor&utm_content=cursor-setup-table-429) |
| 502、超时或流式中断 | [按请求 ID 和时间排查 SSE 链路](https://docs.aifast.hk/troubleshooting/502-stream-disconnected/?utm_source=github&utm_medium=repository&utm_campaign=api-doctor&utm_content=cursor-setup-table-502) |
| 响应太慢 | 先区分网络、排队与生成耗时，再比较满足任务需求的模型 |

---

## 参考

- [Cursor API Key 官方文档](https://cursor.com/help/models-and-usage/api-keys)（2026-10-02 核对：提供商范围、设置入口、请求链路与计费边界）
- [网页模型质量检测](https://docs.aifast.hk/model-check/?utm_source=github&utm_medium=repository&utm_campaign=model-check&utm_content=cursor-setup-reference-model-check)
- [Cursor 自定义 API 配置与功能边界](https://docs.aifast.hk/tools/cursor/?utm_source=github&utm_medium=repository&utm_campaign=integration-guide&utm_content=cursor-setup-reference-docs)
- [Base URL 与 `/v1/v1` 检查](https://docs.aifast.hk/tools/base-url-checker/?utm_source=github&utm_medium=repository&utm_campaign=developer_acquisition&utm_content=cursor-setup-reference-base-url)
- [AI快站模型与价格](https://www.aifast.hk/pricing?utm_source=github&utm_medium=repository&utm_campaign=integration-guide&utm_content=cursor-setup-reference-pricing)
- [AI快站完整接入指南](https://github.com/KKWANG4444/ai-api-proxy-china-guide)
