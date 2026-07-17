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

### Step 3：添加模型

Cursor 的模型选择器里不会自动出现你填的模型名。需要手动在 settings 里的「Models」列表中添加一条，填入精确模型 ID。

只有手动添加的模型，才会出现在 Tab / Cmd+K / Agent 的模型选择下拉菜单。

---

## 2. Cursor 各模式的模型需求

| 模式 | 推荐配置 | 最低要求 |
|:---|:---|:---|
| Tab（补全） | `gpt-5.6-luna` / `deepseek-v4-flash` | 快速文本补全，低延迟模型 |
| Cmd+K（编辑） | `claude-sonnet-5` / `gpt-5.6-terra` | 中等长度上下文 |
| Agent | `claude-opus-4-8` / `gpt-5.6-terra` | 复杂编辑和长上下文 |
| Ask（聊天） | `claude-sonnet-5` | 代码问答 |

一个最小可行的配置是添加一个模型到所有模式。但效果最好的配置是 Agent 用推理能力强的模型，补全用低延迟模型。AI快站的模型目录提供 500+ 选择，按需要搭配。

---

## 3. 常见问题

### 保存时提示 Invalid API Key

- 检查 Key 是否完整复制（AI快站控制台复制，不要手打）
- 检查 Key 是否已在控制台启用
- 检查 Override Base URL 地址是否正确：`https://www.aifast.club/v1`（末尾不要 `/chat/completions`）

### Override Base URL 不生效

Cursor 的部分功能可能走自己的固定端点。如果配置后 Tab 补全不工作，试以下方法：

1. 在 `~/.cursor/` 目录放一个 `.env` 文件：
   ```bash
   echo 'OPENAI_API_BASE=https://www.aifast.club/v1' >> ~/.cursor/.env
   ```
2. 重启 Cursor

### 模型在 Agent 模式下用不了

Agent 模式对流式输出和工具调用依赖较重。如果配置正确但 Agent 经常卡住或报错，可能是该模型对工具调用的支持不够好。建议换一个模型试试。

### Tab 补全很慢或不出

Tab 补全对延迟非常敏感。如果总超时，改用低延迟模型：

| 推荐 | 延迟特点 |
|:---|:---|
| `gpt-5.6-luna` | 快速完成 |
| `deepseek-v4-flash` | 快速完成 |
| `gemini-3.5-flash` | 快速完成 |

### Tab 补全需要额外配置

Cursor 的 Tab 补全默认使用官方端点。Override Base URL 只影响 Chat/Agent 模式。要让 Tab 补全也走自定义接口，需要：

1. **Cursor 0.45+**：Settings > Features > Tab Settings > 选择 "Use your own API key for Tab"
2. **旧版本**：可能不支持 Tab 模式下自定义 provider。升级 Cursor 到最新版。

---

## 4. 验证配置是否生效

配置完成后，打开 **Help > Toggle Developer Tools > Console**，输入：

```javascript
// 查看当前生效的配置
await window.__TAURI__.invoke('get_current_model_config')
```

也可以发一条测试消息确认：

1. 打开 Cmd+K（Ctrl+K）
2. 选 Add 或 Edit 模式
3. 输入 "Write a Python function that calculates fibonacci"
4. 确认模型选择器显示的是你的自定义模型

---

## 5. 排错流程速查

| 问题 | 操作 |
|:---|:---|
| 401 | 检查 API Key |
| 保存失败 | 先 curl 测试 base_url 是否可达 |
| 模型加不了 | 从控制台复制精确 ID，不要写展示名 |
| Agent 卡住 | 换支持 tool calling 的模型 |
| Tab 不工作 | 检查 Cursor 版本+Tab 设置 |
| 响应太慢 | 换低延迟模型 |

---

## 参考

- [Cursor API Key 官方文档](https://docs.cursor.com/settings/api-keys)
- [AI快站模型与价格](https://docs.aifast.club/go/pricing/)
- [AI快站完整接入指南](https://github.com/KKWANG4444/ai-api-proxy-china-guide)
