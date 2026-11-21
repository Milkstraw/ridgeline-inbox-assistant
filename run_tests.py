"""Run every test email through the assistant, check the guardrails, write results.md."""
import json
import re
import sys
from pathlib import Path

from assistant import draft_reply

ALLOWED_DOLLARS = {"$89", "$150"}


def check(test: dict, r: dict) -> list[str]:
    """Return a list of problems with one result (empty = pass)."""
    problems = []
    if r["category"] not in test["expect_category"]:
        problems.append(f"category {r['category']}, expected {' or '.join(test['expect_category'])}")
    if bool(r["flags"]) != test["expect_flag"]:
        problems.append("should be flagged" if test["expect_flag"] else "flagged a routine email")
    bad = set(re.findall(r"\$\d+(?:,\d{3})*", r["draft_reply"])) - ALLOWED_DOLLARS
    if bad:
        problems.append(f"wrote a dollar amount: {', '.join(sorted(bad))}")
    if "Dana" not in r["draft_reply"]:
        problems.append("missing signature")
    return problems


def main():
    sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles/logs default to cp1252
    tests = json.loads(Path("test_emails.json").read_text(encoding="utf-8"))
    rows, details, failed = [], [], 0
    for i, t in enumerate(tests, 1):
        try:
            r = draft_reply(t["email"])
            problems = check(t, r)
        except Exception as e:  # one bad call shouldn't stop the run
            r, problems = {"category": "-", "flags": [], "draft_reply": ""}, [f"error: {e}"]
        failed += bool(problems)
        status = "✅ Pass" if not problems else "❌ " + "; ".join(problems)
        print(f"{i:2}. {t['subject']}: {status}")
        flags = "; ".join(r["flags"]) or "none"
        rows.append(f"| {i} | {t['subject']} | {r['category']} | {flags} | {status} |")
        details.append(f"### {i}. {t['subject']}\n\n**Customer:**\n> {t['email']}\n\n"
                       f"**Category:** {r['category']}  \n**Flags:** {flags}\n\n"
                       f"**Draft reply:**\n```\n{r['draft_reply']}\n```\n")
    summary = f"**{len(tests) - failed} of {len(tests)} passed.**"
    Path("results.md").write_text(
        "# Test Results\n\n" + summary + "\n\n| # | Email | Category | Flags | Result |\n|---|---|---|---|---|\n"
        + "\n".join(rows) + "\n\n## Draft replies\n\n" + "\n".join(details), encoding="utf-8")
    print(summary.strip("*"))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
