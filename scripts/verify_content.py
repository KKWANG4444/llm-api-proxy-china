from pathlib import Path
import re
from urllib.parse import parse_qs, urlsplit


ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS = [
    ROOT / "README.md",
    ROOT / "README_EN.md",
    ROOT / "ABOUT.md",
    ROOT / "ABOUT_EN.md",
    ROOT / "llms.txt",
    ROOT / "llms-full.txt",
]
ERRORS = []


def check(condition, message):
    if not condition:
        ERRORS.append(message)


for document in DOCUMENTS:
    check(document.is_file(), "missing required file: %s" % document.relative_to(ROOT))

contents = {document.name: document.read_text(encoding="utf-8") for document in DOCUMENTS}
combined = "\n".join(contents.values())

check("https://www.aifast.hk/v1" in combined, "missing AIFast Base URL")
check(
    contents["README.md"].startswith("# 国内 AI API 中转站检测："),
    "Chinese README must retain the AI API relay testing intent",
)
check(
    all(keyword in contents["README.md"][:3500] for keyword in ("OpenAI API 中转", "Claude API 中转", "Gemini API 中转", "模型质量检测")),
    "Chinese README hero is missing relay testing search intent",
)
check(
    contents["llms.txt"].startswith("# AI API relay model quality verification")
    and contents["llms-full.txt"].startswith("# AI API relay model quality verification"),
    "machine-readable files must retain the relay verification intent",
)
for stale_pattern in (r"572\s*(?:个\s*模型|models?)", r"GPT[-‐‑‒–—― .]?5\.5", r"Claude[-‐‑‒–—― .]?4\.7", r"Claude[-‐‑‒–—― .]?Fable[-‐‑‒–—― .]?5"):
    check(
        re.search(stale_pattern, combined, flags=re.IGNORECASE) is None,
        "stale model count, model name or repository positioning remains: %s" % stale_pattern,
    )
for document_name in ("README.md", "README_EN.md", "llms.txt", "llms-full.txt"):
    check("500+" in contents[document_name], "%s is missing the current 500+ model-catalog wording" % document_name)
for document_name in ("README.md", "llms.txt"):
    check(
        re.search(r"GPT[-‐‑‒–—― .]?5\.6", contents[document_name], flags=re.IGNORECASE) is not None,
        "%s is missing the current GPT-5.6 model-family wording" % document_name,
    )
for absolute_claim in ("Every model supports its official API interface", "All OpenAI-compatible clients are supported"):
    check(absolute_claim not in combined, "unsupported absolute compatibility claim is still present: %s" % absolute_claim)
check("https://docs.aifast.hk/tools/codex/" in combined, "missing Codex setup entry")
check("https://docs.aifast.hk/en/payment/" in combined, "missing international payment entry")
check(
    all(token in contents["README.md"][:2200] for token in ("llm-hero-model-check", "llm-hero-report-guide", "401", "404", "429", "5xx")),
    "Chinese README hero must route users from model check to report interpretation and error-specific guides",
)
check(
    contents["README.md"].find("llm-hero-model-check") < contents["README.md"].find("assets/social-preview.png"),
    "Chinese README hero image blocks the primary model-check route",
)
check(
    "https://docs.aifast.hk/guides/openai-compatible-api/" in contents["README.md"]
    and "https://docs.aifast.hk/en/guides/openai-compatible-api/" in contents["README_EN.md"],
    "missing Chinese or English OpenAI Compatible setup entry",
)
check(
    "https://docs.aifast.hk/tools/cursor/" in contents["README.md"]
    and "https://docs.aifast.hk/en/tools/cursor/" in contents["README_EN.md"],
    "missing Chinese or English Cursor setup entry",
)
check(
    "https://docs.aifast.hk/tools/cursor2api/?utm_source=github" in contents["README.md"]
    and "https://docs.aifast.hk/troubleshooting/model-not-found/?utm_source=github" in contents["README.md"],
    "missing Cursor2API or model-not-found high-intent deep link",
)
check(
    "https://docs.aifast.hk/troubleshooting/codex-gateway-checklist/" in combined,
    "missing Codex troubleshooting entry",
)
check("https://example.com/v1" not in combined, "placeholder Base URL is still present")
check(
    contents["README_EN.md"].startswith("# LLM API gateway verification and troubleshooting"),
    "English README must retain its verification and troubleshooting intent",
)
for required_section in (
    "## Choose the failure you actually have",
    "## Verify each protocol layer",
    "## Production acceptance report",
    "## Disclosure",
):
    check(required_section in contents["README_EN.md"], "English README is missing: %s" % required_section)
for duplicated_setup_section in (
    "## Quick start",
    "## Model IDs verified in the public catalog",
    "## Tool configuration",
):
    check(
        duplicated_setup_section not in contents["README_EN.md"],
        "English troubleshooting README regressed into a general setup guide: %s" % duplicated_setup_section,
    )
for expected in (
    "⭐️ 1 AIFast Credit = US$1",
    "funded in USD",
    "credited 1:1",
    "console and checkout page",
):
    check(expected in combined, "missing new-site funding fact: %s" % expected)
for document_name in ("README_EN.md", "ABOUT_EN.md", "llms.txt", "llms-full.txt"):
    check("US$1" in contents[document_name], "%s is missing the USD 1:1 funding rule" % document_name)
for document_name in ("README.md", "ABOUT.md"):
    check("⭐️ 1 AIFast Credit = US$1" in contents[document_name], "%s is missing the USD 1:1 funding rule" % document_name)
for stale_payment_term in ("0.75元", "CNY 0.75", "US$0.11", "0.07 USDC", "0.07 USDT", "9.90折", "9.85折", "9.80折"):
    check(stale_payment_term not in combined, "stale payment rule is still present: %s" % stale_payment_term)
for stale_credit_term in ("AIFast balance unit", "1 balance unit", "1刀", "100刀", "500刀", "1000刀", "◈"):
    check(stale_credit_term not in combined, "stale AIFast Credit term is still present: %s" % stale_credit_term)
for forbidden_amount in ("74.25", "369.38", "735.00"):
    check(forbidden_amount not in combined, "specific settlement amount is still present: %s" % forbidden_amount)
for stale_payment_claim in (
    "International users can pay only with cryptocurrency",
    "Fiat payment is not available to international users",
    "国际用户只能使用加密货币",
    "仅支持加密货币充值",
):
    check(stale_payment_claim not in combined, "stale international payment claim is still present: %s" % stale_payment_claim)
for stale_domain in ("www.aifast.club", "docs.aifast.club"):
    check(stale_domain not in combined, "stale AIFast domain is still present: %s" % stale_domain)

wrong_campaign_paths = (
    "/start/",
    "/models/model-selection/",
    "/guides/openai-compatible-api/",
    "/tools/codex/",
    "/troubleshooting/codex-gateway-checklist/",
)

for name in ("README.md", "README_EN.md"):
    source = contents[name]
    for url in re.findall(r"https://docs\.aifast\.hk/[^)\s]+", source):
        parsed = urlsplit(url)
        campaign = parse_qs(parsed.query).get("utm_campaign", [""])[0]
        if parsed.path in wrong_campaign_paths and campaign == "model-check":
            ERRORS.append("%s misclassifies %s as model-check" % (name, parsed.path))

    for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", source):
        target = target.strip().strip("<>")
        if not target or target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        local_path = target.split("#", 1)[0].split("?", 1)[0]
        if local_path and not (ROOT / local_path).is_file():
            ERRORS.append("%s has missing local link: %s" % (name, local_path))

if ERRORS:
    print("Content verification failed:")
    for error in ERRORS:
        print("- " + error)
    raise SystemExit(1)

print("Content verification passed: Codex entries, UTM campaigns and local links are valid.")
