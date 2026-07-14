# AIFast API Doctor

A dependency-free diagnostic CLI for OpenAI-compatible endpoints. It checks authentication, `/v1/models`, and an optional chat completion without printing the API key.

## Run

```bash
export AIFAST_API_KEY="your-key"
python3 tools/aifast_api_doctor.py
```

Test one exact model ID:

```bash
python3 tools/aifast_api_doctor.py --model "model-id-from-console"
```

Test another OpenAI-compatible endpoint:

```bash
python3 tools/aifast_api_doctor.py \
  --base-url "https://example.com/v1" \
  --api-key "$OPENAI_API_KEY"
```

Machine-readable report:

```bash
python3 tools/aifast_api_doctor.py --model "model-id" --json
```

## What the result means

| Result | Next check |
|:---|:---|
| 401 | API key, Bearer authentication, account status |
| 403 | Permissions, access policy, network restrictions |
| 404 | Base URL ending in `/v1`, exact model ID |
| 429 | Concurrency, retry backoff, quota or balance |
| 5xx | Retry with a cap, preserve timestamp and response |
| Network/TLS | DNS, proxy, firewall and certificate chain |

The tool reports the measured request time for that run. It does not turn a single request into a long-term latency or uptime claim.

## Privacy

- API keys are used only in request headers.
- Keys are not written to disk.
- Keys are not included in JSON reports or signup links.
- Keep reports free of private prompts and business data before posting them in an issue.

## Tests

```bash
python3 -m pytest tests/test_aifast_api_doctor.py -q
```

[Create an AIFast account](https://www.aifast.club/register?utm_source=github&utm_medium=repository&utm_campaign=api-doctor&utm_content=tool-docs) after confirming that this endpoint fits your application. The model catalog and maintenance state can change; use the current console as the source of truth.
