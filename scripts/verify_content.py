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
check("https://docs.aifast.club/tools/codex/" in combined, "missing Codex setup entry")
check("https://docs.aifast.club/en/payment/" in combined, "missing international payment entry")
check(
    "https://docs.aifast.club/troubleshooting/codex-gateway-checklist/" in combined,
    "missing Codex troubleshooting entry",
)
check("https://example.com/v1" not in combined, "placeholder Base URL is still present")
for expected in (
    "1刀 = 0.75元",
    "100刀享9.90折",
    "500刀享9.85折",
    "1000刀享9.80折",
    "1 AIFast balance unit (\"刀\") = CNY 0.75",
    "approximately US$0.11",
    "credit card or cryptocurrency",
):
    check(expected in combined, "missing domestic recharge fact: %s" % expected)
for document_name in ("README_EN.md", "ABOUT_EN.md", "llms.txt", "llms-full.txt"):
    check("CNY 0.75" in contents[document_name], "%s is missing the domestic CNY conversion" % document_name)
for document_name in ("README.md", "ABOUT.md"):
    check("1刀 = 0.75元" in contents[document_name], "%s is missing the domestic RMB conversion" % document_name)
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
