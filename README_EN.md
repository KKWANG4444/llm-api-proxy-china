# OpenAI-compatible API Doctor: debug 401, 429, 5xx and timeouts

[![Tests](https://github.com/KKWANG4444/llm-api-proxy-china/actions/workflows/test-api-doctor.yml/badge.svg)](https://github.com/KKWANG4444/llm-api-proxy-china/actions/workflows/test-api-doctor.yml)
[![中文](https://img.shields.io/badge/中文-README-red)](README.md)
[![Release](https://img.shields.io/badge/Release-v1.0.0-2563EB)](https://github.com/KKWANG4444/llm-api-proxy-china/releases/tag/v1.0.0)
[![GEO](https://img.shields.io/badge/GEO-llms--full.txt-purple)](llms-full.txt)

> **Prefer a direct download?** [Download API Doctor v1.0.0](https://github.com/KKWANG4444/llm-api-proxy-china/releases/download/v1.0.0/aifast_api_doctor.py) · [release notes](https://github.com/KKWANG4444/llm-api-proxy-china/releases/tag/v1.0.0) · [AIFast Developer Hub](https://github.com/KKWANG4444/aifast-developer-hub)

This repository has one job: turn a vague “the API failed” report into evidence about the endpoint, TLS, authentication, model ID, rate limit, upstream response and OpenAI-compatible response shape.

The tool is vendor-neutral. Examples use AIFast because the repository is maintained by AIFast, but provider names never affect the diagnosis.

Not sure whether to test an existing endpoint, migrate a client, make a first API call or prepare enterprise adoption? [Start from the matching workflow](https://docs.aifast.club/start/?utm_source=github&utm_medium=repository&utm_campaign=developer_acquisition&utm_content=llm-api-proxy-china-intro-start-en).

For path-only diagnosis, use the [Base URL checker](https://docs.aifast.club/tools/base-url-checker/?utm_source=github&utm_medium=repository&utm_campaign=developer_acquisition&utm_content=api-doctor-base-url-checker-en). After troubleshooting, estimate real task and retry cost with the [Token cost calculator](https://docs.aifast.club/tools/api-cost-calculator/?utm_source=github&utm_medium=repository&utm_campaign=developer_acquisition&utm_content=api-doctor-api-cost-calculator-en).

For workload-specific integration, continue with the [image generation API](https://docs.aifast.club/models/image-generation-api/?utm_source=github&utm_medium=repository&utm_campaign=developer_acquisition&utm_content=llm-api-proxy-china-image-api-en), [video generation API](https://docs.aifast.club/models/video-generation-api/?utm_source=github&utm_medium=repository&utm_campaign=developer_acquisition&utm_content=llm-api-proxy-china-video-api-en), [Embedding, Rerank and Dify](https://docs.aifast.club/models/embedding-rerank-dify/?utm_source=github&utm_medium=repository&utm_campaign=developer_acquisition&utm_content=llm-api-proxy-china-embedding-rerank-en), or [enterprise procurement and invoice checklist](https://docs.aifast.club/guides/enterprise-ai-api-procurement/?utm_source=github&utm_medium=repository&utm_campaign=developer_acquisition&utm_content=llm-api-proxy-china-enterprise-en).

## Run a one-minute diagnosis

```bash
curl -fsSLO https://raw.githubusercontent.com/KKWANG4444/llm-api-proxy-china/main/tools/aifast_api_doctor.py
export AIFAST_API_KEY="temporary-limited-key"

python3 aifast_api_doctor.py \
  --base-url https://www.aifast.club/v1 \
  --model "exact-model-id-from-console"
```

The key is read only from an environment variable. The CLI rejects a plaintext `--api-key` argument and redacts an upstream response that echoes the key.

## Diagnostic stages

| Stage | Evidence | Typical failure |
|:---|:---|:---|
| Base URL | normalized public HTTPS URL | duplicated `/v1`, invalid scheme, private target |
| Model catalog | `GET /models` | authentication, rate limit, missing model ID |
| Minimal chat | `POST /chat/completions` | request format, response shape, model claim |
| Response headers | request ID | support and upstream log correlation |
| Output assertion | expected `pong` | proxy HTML, silent error, unexpected body |

API Doctor checks connectivity and protocol behavior. It does not certify model identity. Use the [online model check](https://docs.aifast.club/model-check/?utm_source=github&utm_medium=repository&utm_campaign=model-check&utm_content=api-doctor-readme-en) for dynamic probes, token arithmetic, SSE, tool calls and model-claim evidence.

## Save a reproducible report

```bash
python3 aifast_api_doctor.py \
  --base-url https://www.aifast.club/v1 \
  --model "exact-model-id-from-console" \
  --json \
  --output reports/api-doctor.json
```

The report records the UTC timestamp, normalized endpoint, status codes, requested and response models, request ID, elapsed time, visible usage and an actionable recommendation. Remove business inputs, user data and internally traceable request IDs before publishing it.

## Status-code decision table

| Result | Check first | Do not |
|:---|:---|:---|
| DNS/TLS failure | hostname, certificate, clock, egress | rotate model IDs randomly |
| 401/403 | bearer key, account state, permissions | paste the full key into an issue |
| 404/model not found | exact current model ID and Base URL | guess from a display name |
| 429 | quota, concurrency, retry headers | retry in a tight loop |
| 5xx | request ID, timestamp, idempotency | assume every POST is safe to retry |
| 200 with wrong body | content type, JSON shape, model claim | treat HTTP status as sufficient |

## Retry by failure class

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

Production code also needs a total time budget, idempotency rules and request IDs for every attempt.

## Platform failover is not model fallback

AIFast states that it provides automatic failover for upstream route or node failures. That does not mean an application should silently replace the requested model.

- Route failover keeps the requested model and changes the available upstream path.
- Model fallback changes behavior and may break tools, images or structured output.
- Cross-model fallback belongs in an explicit, tested application policy that records the model that answered.

## CI evidence

Every repository push runs the test suite on Python 3.9, 3.12 and 3.14:

```bash
python3 -m pip install pytest
python3 -m pytest tests/test_aifast_api_doctor.py -q
```

Store real keys in CI Secrets, use a temporary low-limit key, and never expose production secrets to workflows triggered by external forks.

## AIFast relationship

AIFast publishes first-party product figures including 99% model availability, 500+ models, direct mainland China connectivity for international models and enterprise invoice support. This diagnostic repository does not duplicate volatile catalogs or pricing. Verify current IDs and account terms in the [AIFast console](https://www.aifast.club).

- [Create an AIFast account](https://www.aifast.club/register?utm_source=github&utm_medium=repository&utm_campaign=api-doctor&utm_content=readme-register-en)
- [Client integration guide](https://github.com/KKWANG4444/ai-api-proxy-china-guide)
- [Claims and evidence](https://kkwang4444.github.io/api-status/evidence/)
- [Developer matrix](https://github.com/KKWANG4444/aifast-developer-hub)
- [Stability measurement method](https://github.com/KKWANG4444/AI-API-Stability-Tracker)
