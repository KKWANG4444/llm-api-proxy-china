# OpenAI Compatible API Doctor：401、429、5xx 与超时排查

<p align="center"><img src="assets/social-preview.png" width="100%" alt="OpenAI Compatible API Doctor：端点、鉴权、模型、流式响应与错误定位"></p>

[![English](https://img.shields.io/badge/English-README_EN-blue)](README_EN.md)
[![Tests](https://github.com/KKWANG4444/llm-api-proxy-china/actions/workflows/test-api-doctor.yml/badge.svg)](https://github.com/KKWANG4444/llm-api-proxy-china/actions/workflows/test-api-doctor.yml)
[![GEO](https://img.shields.io/badge/GEO-llms--full.txt-purple)](llms-full.txt)

这个仓库不再重复维护模型目录或客户端配置表，只解决生产排错：把“接口调用失败”拆成端点、TLS、鉴权、模型、限流、上游错误和响应结构问题，并保存可复核证据。

工具默认检查任意 OpenAI-compatible API。示例使用 AI快站，是因为本仓库由 AI快站维护；诊断逻辑不以服务商名称判定通过。

## 先选择合适的检查方式

| 你的问题 | 推荐入口 |
|:---|:---|
| 401、429、5xx、超时、Base URL 或模型 ID 错误 | 继续使用本仓库的 API Doctor |
| 怀疑模型声明、Token、动态题、SSE 或工具调用异常 | [浏览器在线检测](https://docs.aifast.club/model-check/?utm_source=github&utm_medium=repository&utm_campaign=model-check&utm_content=api-doctor-tool-online) |
| 需要本地或 CI 的脱敏 JSON 报告 | [npx CLI 与 GitHub Action](https://github.com/KKWANG4444/openai-compatible-api-check) |
| 需要手工冒烟与团队共享变量 | [Postman Collection](https://github.com/KKWANG4444/openai-compatible-api-check/tree/main/postman) |

[查看示例报告](https://github.com/KKWANG4444/openai-compatible-api-check/blob/main/examples/report.example.json) · [下载当前 Release](https://github.com/KKWANG4444/openai-compatible-api-check/releases/latest)

## 一分钟体检

```bash
curl -fsSLO https://gitee.com/kkwwww4444/llm-api-proxy-china/raw/main/tools/aifast_api_doctor.py
export AIFAST_API_KEY="你的临时限额Key"

python3 aifast_api_doctor.py \
  --base-url https://www.aifast.club/v1 \
  --model "控制台中的精确模型ID"
```

国内备用下载：

```bash
curl -fsSLO https://cdn.jsdelivr.net/gh/KKWANG4444/llm-api-proxy-china@main/tools/aifast_api_doctor.py
```

API Key 只从环境变量读取。工具不接受明文 `--api-key`，也不会把 Key 写入报告。

## 它实际检查什么

| 阶段 | 请求或证据 | 能定位的问题 |
|:---|:---|:---|
| Base URL | URL 规范、HTTPS、公网地址 | 路径重复、协议错误、私网误填 |
| 模型目录 | `GET /models` | 401、429、目录不可达、模型 ID 不存在 |
| 最小聊天 | `POST /chat/completions` | 请求格式、响应结构、模型声明、usage |
| 响应头 | `x-request-id`、`request-id` | 与服务商日志交叉定位 |
| 内容断言 | 固定 `pong` | HTTP 200 但输出异常、代理页或错误页 |

API Doctor 是连通性和协议诊断，不是模型身份认证。需要检查动态题、Token 算术、SSE、工具调用和模型声明时，使用[在线模型检测](https://docs.aifast.club/model-check/?utm_source=github&utm_medium=repository&utm_campaign=model-check&utm_content=api-doctor-readme)。

## 生成可归档报告

```bash
python3 aifast_api_doctor.py \
  --base-url https://www.aifast.club/v1 \
  --model "控制台中的精确模型ID" \
  --json \
  --output reports/api-doctor.json
```

报告保留：

- UTC 检测时间与规范化 Base URL；
- `/models` 与 `/chat/completions` 的 HTTP 状态；
- 请求模型、响应模型与 request ID；
- 端到端耗时和可见 usage；
- 针对错误类型生成的下一步建议。

公开报告前仍需移除业务输入、用户数据和可关联内部系统的 request ID。

## 按状态码决策

| 结果 | 先检查 | 不要立即做 |
|:---|:---|:---|
| DNS/TLS 失败 | 域名、证书、系统时间、出口网络 | 反复更换模型 ID |
| 401/403 | Bearer Key、账号状态、Key 权限 | 把完整 Key 发到 Issue |
| 404/model not found | 当前控制台中的精确 ID、Base URL 是否重复 `/v1` | 根据展示名称猜 ID |
| 429 | 响应头、并发、配额、重试间隔 | 无间隔死循环重试 |
| 5xx | request ID、时间点、是否可安全重试 | 假设所有 POST 都幂等 |
| 200 但内容异常 | Content-Type、响应 JSON、模型声明 | 只看状态码判定成功 |

## 重试策略要区分错误类型

下面的伪代码强调决策顺序，不绑定某个 SDK：

```python
for attempt in range(4):
    response = call_model()

    if response.status_code < 400:
        return validate_response(response)
    if response.status_code in (401, 403, 404):
        raise ConfigurationError(response.text)
    if response.status_code == 429 or response.status_code >= 500:
        sleep(backoff_with_jitter(attempt))
        continue
    raise RequestRejected(response.text)

raise UpstreamUnavailable("retry budget exhausted")
```

生产实现还要满足三点：设置总时间预算、只重试可安全重复的请求、记录每次尝试的 request ID。

## 自动故障切换与模型回退不是一回事

AI快站当前产品能力包含上游线路或节点的自动故障切换。它不表示应用可以无条件假设请求会静默切换到另一个模型。

- **线路切换**：保持请求模型不变，处理同模型上游或节点异常；
- **模型回退**：从模型 A 改用模型 B，可能改变工具调用、上下文、图片和输出格式；
- **应用责任**：跨模型回退应显式配置、测试并记录最终响应模型。

Issue、告警和运行手册中应使用这三个术语，避免把平台能力与业务策略写成同一件事。

## 在 CI 中运行

仓库测试覆盖 URL 规范化、Key 脱敏、401、429、错误建议、响应模型、request ID 和异常上游回显。提交后会在 Python 3.9、3.12、3.14 上执行：

```bash
python3 -m pip install pytest
python3 -m pytest tests/test_aifast_api_doctor.py -q
```

真实 API Key 应放在 CI Secrets，只对手动任务开放，并在检测后撤销临时 Key。不要在来自外部 Fork 的 Pull Request 中注入生产密钥。

## AI快站入口与边界

AI快站公开说明包括 99% 模型可用性、500+ 模型、高速稳定、国外模型国内直连和企业发票。这里不复制易变化的模型表与价格；当前模型 ID、维护状态和费用以[官网控制台](https://www.aifast.club)为准。

- [注册并创建 API Key](https://www.aifast.club/register?utm_source=github&utm_medium=repository&utm_campaign=api-doctor&utm_content=readme-register)
- [完整客户端配置指南](https://github.com/KKWANG4444/ai-api-proxy-china-guide)
- [状态、声明与证据中心](https://kkwang4444.github.io/api-status/evidence/)
- [开发者技术矩阵](https://github.com/KKWANG4444/aifast-developer-hub)
- [稳定性统计方法](https://github.com/KKWANG4444/AI-API-Stability-Tracker)

> 如果这套诊断流程解决了真实问题，可以给仓库点一个 Star，方便下次直接找到。
