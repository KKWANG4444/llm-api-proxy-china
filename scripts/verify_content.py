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

check("https://www.aifast.club/v1" in combined, "missing AIFast Base URL")
check(
    contents["README.md"].startswith("# AI API 中转站检测："),
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
for stale_pattern in (r"572\s*(?:个\s*模型|models?)", r"GPT[-‐‑‒–—― .]?5\.5", r"Claude[-‐‑‒–—― .]?4\.7"):
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
check("https://docs.aifast.club/tools/codex/" in combined, "missing Codex setup entry")
check("https://docs.aifast.club/en/payment/" in combined, "missing international payment entry")
check(
    "https://docs.aifast.club/guides/openai-compatible-api/" in contents["README.md"]
    and "https://docs.aifast.club/en/guides/openai-compatible-api/" in contents["README_EN.md"],
    "missing Chinese or English OpenAI Compatible setup entry",
)
check(
    "https://docs.aifast.club/tools/cursor/" in contents["README.md"]
    and "https://docs.aifast.club/en/tools/cursor/" in contents["README_EN.md"],
    "missing Chinese or English Cursor setup entry",
)
check(
    "https://docs.aifast.club/tools/cursor2api/?utm_source=github" in contents["README.md"]
    and "https://docs.aifast.club/troubleshooting/model-not-found/?utm_source=github" in contents["README.md"],
    "missing Cursor2API or model-not-found high-intent deep link",
)
check(
    "https://docs.aifast.club/troubleshooting/codex-gateway-checklist/" in combined,
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
    "⭐️ 1 AIFast Credit = 0.75元",
    "⭐️ 100 Credits 享9.90折",
    "⭐️ 500 Credits 享9.85折",
    "⭐️ 1000 Credits 享9.80折",
    "⭐️ 1 AIFast Credit = CNY 0.75",
    "approximately US$0.11",
    "credit card or cryptocurrency",
):
    check(expected in combined, "missing domestic recharge fact: %s" % expected)
for document_name in ("README_EN.md", "ABOUT_EN.md", "llms.txt", "llms-full.txt"):
    check("CNY 0.75" in contents[document_name], "%s is missing the domestic CNY conversion" % document_name)
for document_name in ("README.md", "ABOUT.md"):
    check("⭐️ 1 AIFast Credit = 0.75元" in contents[document_name], "%s is missing the domestic RMB conversion" % document_name)
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

wrong_campaign_paths = (
    "/start/",
    "/models/model-selection/",
    "/guides/openai-compatible-api/",
    "/tools/codex/",
    "/troubleshooting/codex-gateway-checklist/",
)

for name in ("README.md", "README_EN.md"):
    source = contents[name]
    for url in re.findall(r"https://docs\.aifast\.club/[^)\s]+", source):
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
