"""Seeds GitHub issues in the fork for remediation.
Run once: python scripts/create_issues.py
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx

from app.config import settings

ISSUES = [
    {
        "title": "Add a CONTRIBUTING.md file",
        "body": (
            "We don't have a `CONTRIBUTING.md` file at the root of the repo.\n\n"
            "Please create one that includes:\n"
            "- A brief welcome message for contributors\n"
            "- How to set up the project locally\n"
            "- How to submit a pull request\n\n"
            "Keep it short and friendly."
        ),
        "labels": ["automation:remediation", "documentation"],
    },
    {
        "title": "Upgrade boto3 to the latest version",
        "body": (
            "The `boto3` library is pinned to an old version in the project dependencies.\n\n"
            "**Task:**\n"
            "Upgrade `boto3` to the latest stable version.\n\n"
            "**Steps:**\n"
            "1. Find all references to `boto3` in `requirements.txt`, `setup.py`, or `pyproject.toml`\n"
            "2. Update the version pin to the latest stable release (`>=1.35.0`)\n"
            "3. Commit and open a pull request with the change"
        ),
        "labels": ["automation:remediation", "tooling"],
    },
    {
        "title": "Replace datetime.utcnow() with timezone-aware alternative",
        "body": (
            "`datetime.utcnow()` is deprecated as of Python 3.12 and will be removed in a future version. "
            "It returns a naive datetime with no timezone info, which can cause bugs when comparing times.\n\n"
            "**Task:**\n"
            "Find all usages of `datetime.utcnow()` in the codebase and replace them with "
            "`datetime.now(timezone.utc)` from the standard library.\n\n"
            "**Steps:**\n"
            "1. Search the repo for all occurrences of `datetime.utcnow()`\n"
            "2. Replace each with `datetime.now(timezone.utc)`\n"
            "3. Ensure `from datetime import datetime, timezone` is imported wherever needed\n"
            "4. Open a pull request with the changes"
        ),
        "labels": ["automation:remediation", "bug"],
    },
]

_COLOR_MAP = {
    "automation:remediation": "e11d48",
    "documentation": "0075ca",
    "tooling": "e4e669",
    "bug": "d73a4a",
}


def ensure_label(repo: str, label: str, headers: dict) -> None:
    url = f"https://api.github.com/repos/{repo}/labels"
    resp = httpx.get(url, headers=headers, timeout=15)
    existing = {item["name"] for item in resp.json()} if resp.status_code == 200 else set()
    if label not in existing:
        httpx.post(
            url,
            headers=headers,
            json={"name": label, "color": _COLOR_MAP.get(label, "0075ca")},
            timeout=15,
        )
        print(f"  Created label: {label}")


def main() -> None:
    repo = settings.github_repo
    headers = {
        "Authorization": f"Bearer {settings.github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    print(f"Seeding issues in {repo}...")

    all_labels: set[str] = set()
    for issue in ISSUES:
        all_labels.update(issue.get("labels", []))
    for label in all_labels:
        ensure_label(repo, label, headers)

    for issue in ISSUES:
        # Create first without the trigger label; adding it separately fires the 'labeled' webhook
        non_trigger = [lbl for lbl in issue.get("labels", []) if lbl != "automation:remediation"]
        resp = httpx.post(
            f"https://api.github.com/repos/{repo}/issues",
            headers=headers,
            json={"title": issue["title"], "body": issue["body"], "labels": non_trigger},
            timeout=15,
        )
        if resp.status_code != 201:
            print(f"  FAILED to create: {resp.status_code} {resp.text}")
            continue

        data = resp.json()
        number = data["number"]
        print(f"  Created issue #{number}: {data['title']}")
        print(f"    URL: {data['html_url']}")

        label_resp = httpx.post(
            f"https://api.github.com/repos/{repo}/issues/{number}/labels",
            headers=headers,
            json={"labels": ["automation:remediation"]},
            timeout=15,
        )
        if label_resp.status_code == 200:
            print("    Trigger label added → webhook fired")
        else:
            print(f"    WARN: could not add trigger label: {label_resp.status_code}")

        time.sleep(30)  # Devin enforces a concurrent session limit; stagger issue creation


if __name__ == "__main__":
    main()
