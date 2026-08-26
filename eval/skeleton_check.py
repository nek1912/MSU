import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

SEEDS_DIR = Path(__file__).parent.parent / "corpus" / "seeds"
CASES_ANSWER = [
    ("What are the eligibility criteria under PMFBY?", "en"),
    ("How are PMFBY claims made after crop loss?", "en"),
    ("What do the model byelaws for PACS cover?", "en"),
    ("What services does a PACS provide to farmers?", "en"),
    ("PMFBY ke antargat paatrata kya hai?", "hi"),
]
CASES_ABSTAIN = [("Who won yesterday's cricket match?", "en"),
                 ("Recommend me a good movie", "hi")]


def api_base() -> str:
    return sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
        "API_BASE", "http://localhost:8000")


def load_seed_urls() -> set[str]:
    """Every citation must point at a URL present in the seed manifest
    (P0-4): the gate verifies sources, not just shapes."""
    urls = set()
    for path in SEEDS_DIR.glob("*.md"):
        for line in path.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^url:\s*(\S+)", line)
            if m:
                urls.add(m.group(1))
                break
    return urls


def chat(base: str, q: str, lang: str) -> dict:
    req = urllib.request.Request(
        f"{base}/chat", method="POST",
        data=json.dumps({"question": q, "session_id": str(time.time_ns()),
                         "language": lang, "state": None}).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def main() -> int:
    base = api_base()
    allowed = load_seed_urls()
    results = {"passed": True, "api": base, "answers": [], "abstains": []}
    for q, lang in CASES_ANSWER:
        body = chat(base, q, lang)
        ok = (not body["abstained"]
              and len(body["citations"]) >= 1
              and all(c["url"] in allowed for c in body["citations"]))
        results["passed"] &= ok
        results["answers"].append({"q": q, "ok": ok, "citations": body["citations"]})
    for q, lang in CASES_ABSTAIN:
        body = chat(base, q, lang)
        ok = body["abstained"] and body["citations"] == []
        results["passed"] &= ok
        results["abstains"].append({"q": q, "ok": ok})
    os.makedirs("eval/reports", exist_ok=True)
    with open("eval/reports/skeleton.json", "w") as f:
        json.dump(results, f, indent=2)
    print(json.dumps(results, indent=2))
    return 0 if results["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
