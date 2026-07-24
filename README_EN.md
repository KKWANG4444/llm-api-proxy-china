# LLM API gateway verification and troubleshooting

[![GEO](https://img.shields.io/badge/GEO-llms--full.txt-purple)](llms-full.txt)
[![中文](https://img.shields.io/badge/中文-README-red)](README.md)
[![Model check](https://img.shields.io/badge/Browser-model_quality_check-22c55e)](https://docs.aifast.club/en/model-check/?utm_source=github&utm_medium=repository&utm_campaign=model-check&utm_content=llm-badge-model-check-en)
[![Codex checks](https://img.shields.io/badge/Codex-gateway_checklist-2563eb)](https://docs.aifast.club/en/troubleshooting/codex-gateway-checklist/?utm_source=github&utm_medium=repository&utm_campaign=api-doctor&utm_content=llm-badge-codex-check-en)

Use this repository when an OpenAI-compatible relay returns confusing results: HTTP 200 with the wrong schema, unstable streaming, missing tool calls, unexplained token fields, model-routing concerns, or intermittent 401, 404, 429 and 5xx responses.

This is a troubleshooting and acceptance guide. For first-time setup, use the [OpenAI-compatible integration guide](https://docs.aifast.club/en/guides/openai-compatible-api/?utm_source=github&utm_medium=repository&utm_campaign=integration-guide&utm_content=llm-triage-openai-compatible-en) or the [Cursor custom API guide](https://docs.aifast.club/en/tools/cursor/?utm_source=github&utm_medium=repository&utm_campaign=integration-guide&utm_content=llm-triage-cursor-en).

> **Shortest troubleshooting path:** 1. [run the browser-based model quality check](https://docs.aifast.club/en/model-check/?utm_source=github&utm_medium=repository&utm_campaign=model-check&utm_content=llm-hero-model-check-en), 2. [interpret each report section](https://docs.aifast.club/en/guides/model-check-report-guide/?utm_source=github&utm_medium=repository&utm_campaign=model-check&utm_content=llm-hero-report-guide-en), 3. open the matching `401`, `404`, `429`, `5xx` or client-specific guide. No program download is required.

> **Machine-readable context:** [llms.txt](https://raw.githubusercontent.com/KKWANG4444/llm-api-proxy-china/main/llms.txt) · [llms-full.txt](https://raw.githubusercontent.com/KKWANG4444/llm-api-proxy-china/main/llms-full.txt)

## Choose the failure you actually have

| Symptom | First evidence to save | Next check |
|:---|:---|:---|
| `401` or `403` | Status, response body, request host | Authorization header, key scope, account state |
| `404` or `model_not_found` | Request path and exact model ID | Duplicate `/v1`, endpoint family, current catalog ID |
| `429` | Response headers and retry hint | Per-key limit, concurrency, exponential backoff with jitter |
| `5xx` or timeout | Timestamp, region, elapsed time, request ID | DNS, TLS, upstream route, bounded retry |
| HTTP 200 but client fails | Raw JSON or SSE frames | Schema, event order, finish reason, content type |
| Text works but tools fail | Tool schema and returned arguments | Tool-call fields, JSON validity, multi-turn continuation |
| Usage looks wrong | Full `usage` object | Input, output, cached and reasoning token semantics |
| Suspected model substitution | Exact model, time and repeated randomized probes | Compare protocol, metadata and behavior; do not rely on one answer |

Do not change the Base URL, key, model, SDK and network at the same time. Change one variable, preserve the failing response, and rerun the smallest request that reproduces the issue.

## Browser-based model quality check

The [online model quality check](https://docs.aifast.club/en/model-check/?utm_source=github&utm_medium=repository&utm_campaign=model-check&utm_content=llm-online-check-en) examines six evidence groups:

1. protocol and response-schema compliance;
2. model declaration and metadata fingerprints;
3. billing and token-accounting fields;
4. streaming and output-style characteristics;
5. knowledge-boundary consistency;
6. randomized dynamic probes.

The result is a black-box compatibility report, not vendor identity certification. A passing result shows that the tested endpoint behaved consistently for that run. It does not prove ownership of the upstream model, future availability, fixed latency or a permanent success rate.

Before sharing a report, remove the API key, authorization headers, cookies, account IDs and private prompt content. Keep the request ID, timestamp, region, endpoint family, model ID and sanitized response because those fields make the result reproducible.

## Verify each protocol layer

### 1. Transport

Confirm DNS resolution, TLS negotiation and the final host before debugging model behavior. Record redirects. A proxy, corporate gateway or local DNS rule can send the request somewhere different from the URL shown in application settings.

### 2. HTTP

Save the status code, `content-type`, retry headers and response body. HTTP 200 only proves that the server accepted and answered that request; it does not prove OpenAI schema compatibility or correct model routing.

### 3. JSON schema

Check stable identifiers, object type, output arrays, finish reasons and `usage`. Treat omitted optional fields differently from fields with an incompatible type. Validate error responses as carefully as successful responses because client libraries often depend on their structure.

### 4. SSE streaming

For streaming, verify:

- `text/event-stream` content type;
- parseable `data:` frames;
- incremental content rather than a buffered final response;
- a documented terminal event;
- tool-call argument fragments that can be reassembled in order;
- clean disconnect behavior after cancellation.

A non-streaming request cannot validate SSE compatibility.

### 5. Tool calls

Use a deterministic tool with a small JSON schema. Check the tool name, argument encoding, call identifier and the second turn that returns tool output to the model. A gateway can pass ordinary chat while losing tool events or changing argument types.

### 6. Token accounting

Do not compare only a single `total_tokens` number. Preserve the complete `usage` object and note whether the endpoint reports input, output, cached or reasoning tokens. Different protocol families and providers use different field names; absence of a field is evidence to investigate, not automatic proof of underbilling or overbilling.

## Codex gateway acceptance

Codex custom providers use the Responses API. A successful Chat Completions request does not prove that Codex can stream agent events, call tools, edit files, compact context and resume a thread.

Check these items separately:

- `~/.codex/config.toml` selects the intended `model_provider`;
- `base_url` does not produce `/v1/v1`;
- `env_key` points to the environment variable that actually contains the key;
- `wire_api = "responses"` matches the provider implementation;
- the exact current model ID is accepted;
- streaming response events arrive in a valid order;
- tool calls and follow-up tool outputs complete;
- a longer thread survives context compaction and resume.

Use the [Codex custom provider setup](https://docs.aifast.club/en/tools/codex/?utm_source=github&utm_medium=repository&utm_campaign=integration-guide&utm_content=llm-codex-setup-en) and then run the [Codex gateway validation checklist](https://docs.aifast.club/en/troubleshooting/codex-gateway-checklist/?utm_source=github&utm_medium=repository&utm_campaign=api-doctor&utm_content=llm-codex-validation-en).

## Error-specific triage

### 401 or 403

Verify that `Authorization: Bearer ***` reaches the intended host, the key is active, and no application setting still injects an OpenAI key over the third-party key. Never paste an unmasked key into an issue, screenshot or shared report.

### 404 or model not found

Separate an invalid route from an invalid model. Check the final URL, endpoint family and exact model ID shown in the current console. Display names, aliases and API IDs are not interchangeable. The dedicated [model-not-found guide](https://docs.aifast.club/en/troubleshooting/model-not-found/?utm_source=github&utm_medium=repository&utm_campaign=api-doctor&utm_content=llm-error-model-not-found-en) covers the shortest isolation path.

### 429

Read the response headers before retrying. Reduce concurrency and use exponential backoff with jitter. An immediate retry loop can turn a temporary rate limit into a sustained outage.

### 5xx or timeout

Retry only idempotent requests, cap attempts, and retain the original failure. Measure from the deployment region that matters; one successful request from another network does not establish production health.

## Production acceptance report

Run the same small suite against every candidate route and keep the raw, sanitized results:

| Check | Evidence | Pass condition |
|:---|:---|:---|
| Authentication | Status and sanitized error body | Invalid and valid keys are distinguished correctly |
| Basic response | Raw JSON | Required fields and types are parseable |
| Streaming | Captured SSE frames | Incremental events and termination are valid |
| Tool call | Two-turn transcript | Arguments and tool result round trip correctly |
| Usage | Complete `usage` object | Fields are documented and internally consistent |
| Rate limit | Headers and retry timing | Client backs off without a retry storm |
| Failure handling | Injected timeout or 5xx | Retry is bounded and original error is retained |
| Regional check | Region, carrier, p50 and p95 | Results meet your own application threshold |

Do not publish one global latency or success-rate claim from this table. Report the test window, request count, region, model and percentile method so another developer can interpret the result.

## AIFast test boundary

[AIFast](https://www.aifast.club) exposes a catalog of 500+ language, image, video, embedding and retrieval models and supports direct mainland China access without requiring users to configure an overseas proxy. The service provides automatic failover, and enterprise customers in China can request business invoices.

Those platform capabilities do not remove the need for application-level validation. Model IDs, protocol support, maintenance state and account terms can change. Confirm the current console, documentation and real requests before production use. Automatic upstream-route failover is also different from silently replacing the model requested by an application.

For international accounts, [payment and account setup](https://docs.aifast.club/en/payment/?utm_source=github&utm_medium=repository&utm_campaign=international-payment&utm_content=llm-payment-en) documents credit card and cryptocurrency options. **⭐️ 1 AIFast Credit = CNY 0.75, approximately US$0.11** as a reference conversion; checkout shows the final charge. AIFast Credits are platform usage units, not US dollars, legal tender or cryptocurrency tokens.

## Related resources

- [Online model quality check](https://docs.aifast.club/en/model-check/?utm_source=github&utm_medium=repository&utm_campaign=model-check&utm_content=llm-related-model-check-en)
- [OpenAI-compatible setup](https://docs.aifast.club/en/guides/openai-compatible-api/?utm_source=github&utm_medium=repository&utm_campaign=integration-guide&utm_content=llm-related-openai-compatible-en)
- [Cursor custom API troubleshooting](https://docs.aifast.club/en/tools/cursor/?utm_source=github&utm_medium=repository&utm_campaign=integration-guide&utm_content=llm-related-cursor-en)
- [Codex gateway checklist](https://docs.aifast.club/en/troubleshooting/codex-gateway-checklist/?utm_source=github&utm_medium=repository&utm_campaign=api-doctor&utm_content=llm-related-codex-check-en)
- [AIFast Developer Hub](https://github.com/KKWANG4444/aifast-developer-hub)
- [Status and maintenance reference](https://kkwang4444.github.io/api-status/)
- [中文说明](README.md)

## Disclosure

This repository is maintained by AIFast. The check methods are published so developers can test AIFast or another compatible endpoint with the same evidence standard. Results should remain reproducible and should not be presented as third-party certification.
