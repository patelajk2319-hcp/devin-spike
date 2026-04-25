"""
Seeds GitHub issues in the fork for remediation.
Run once: python scripts/create_issues.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from app.config import settings

ISSUES = [
    {
        "title": "[Security] Upgrade Pillow to patch CVE-2023-44271 (uncontrolled resource consumption)",
        "body": (
            "**Vulnerability:** CVE-2023-44271\n"
            "**Package:** Pillow < 10.0.1\n"
            "**Severity:** High\n\n"
            "Pillow versions prior to 10.0.1 are vulnerable to uncontrolled resource consumption "
            "via crafted image files. Upgrade `Pillow` to `>=10.0.1` in requirements files.\n\n"
            "**Acceptance criteria:**\n"
            "- `Pillow>=10.0.1` in all relevant requirements files\n"
            "- Existing image-handling tests pass\n"
            "- No other dependency conflicts introduced"
        ),
        "labels": ["automation:remediation", "security"],
    },
    {
        "title": "[Security] Upgrade cryptography package to patch CVE-2023-49083 (NULL pointer dereference)",
        "body": (
            "**Vulnerability:** CVE-2023-49083\n"
            "**Package:** cryptography < 41.0.6\n"
            "**Severity:** High\n\n"
            "The `cryptography` package before 41.0.6 is vulnerable to a NULL pointer dereference "
            "when loading PKCS7 certificates. Upgrade to `>=41.0.6`.\n\n"
            "**Acceptance criteria:**\n"
            "- `cryptography>=41.0.6` in all relevant requirements files\n"
            "- No dependency conflicts introduced"
        ),
        "labels": ["automation:remediation", "security"],
    },
    {
        "title": "[Security] Upgrade Werkzeug to patch CVE-2023-46136 (DoS via multipart parsing)",
        "body": (
            "**Vulnerability:** CVE-2023-46136\n"
            "**Package:** Werkzeug < 3.0.1\n"
            "**Severity:** High\n\n"
            "Werkzeug before 3.0.1 allows a denial-of-service via specially crafted multipart data. "
            "Upgrade `Werkzeug` to `>=3.0.1`.\n\n"
            "**Acceptance criteria:**\n"
            "- `Werkzeug>=3.0.1` pinned in requirements\n"
            "- Flask compatibility verified\n"
            "- Existing tests pass"
        ),
        "labels": ["automation:remediation", "security"],
    },
    {
        "title": "[Security] Upgrade requests to patch CVE-2023-32681 (credential leakage on redirect)",
        "body": (
            "**Vulnerability:** CVE-2023-32681\n"
            "**Package:** requests < 2.31.0\n"
            "**Severity:** Medium\n\n"
            "`requests` before 2.31.0 leaks `Proxy-Authorization` headers to the destination server "
            "when following redirects to different hosts. Upgrade to `>=2.31.0`.\n\n"
            "**Acceptance criteria:**\n"
            "- `requests>=2.31.0` in all requirements files\n"
            "- No regressions in HTTP client usage"
        ),
        "labels": ["automation:remediation", "security"],
    },
    {
        "title": "[Security] Upgrade sqlparse to patch CVE-2024-4340 (ReDoS vulnerability)",
        "body": (
            "**Vulnerability:** CVE-2024-4340\n"
            "**Package:** sqlparse < 0.5.0\n"
            "**Severity:** High\n\n"
            "`sqlparse` before 0.5.0 is vulnerable to a Regular Expression Denial of Service (ReDoS) "
            "via deeply nested SQL expressions. Upgrade to `>=0.5.0`.\n\n"
            "**Acceptance criteria:**\n"
            "- `sqlparse>=0.5.0` in requirements\n"
            "- Existing SQL parsing tests pass"
        ),
        "labels": ["automation:remediation", "security"],
    },
]


def ensure_label(repo: str, label: str, headers: dict):
    color_map = {
        "automation:remediation": "e11d48",
        "security": "d93f0b",
    }
    url = f"https://api.github.com/repos/{repo}/labels"
    resp = httpx.get(url, headers=headers, timeout=15)
    existing = {l["name"] for l in resp.json()} if resp.status_code == 200 else set()
    if label not in existing:
        httpx.post(
            url,
            headers=headers,
            json={"name": label, "color": color_map.get(label, "0075ca")},
            timeout=15,
        )
        print(f"  Created label: {label}")


def main():
    repo = settings.github_repo
    headers = {
        "Authorization": f"Bearer {settings.github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    print(f"Seeding issues in {repo}...")

    all_labels = set()
    for issue in ISSUES:
        all_labels.update(issue.get("labels", []))
    for label in all_labels:
        ensure_label(repo, label, headers)

    for issue in ISSUES:
        resp = httpx.post(
            f"https://api.github.com/repos/{repo}/issues",
            headers=headers,
            json={
                "title": issue["title"],
                "body": issue["body"],
                "labels": issue.get("labels", []),
            },
            timeout=15,
        )
        if resp.status_code == 201:
            data = resp.json()
            print(f"  Created issue #{data['number']}: {data['title']}")
            print(f"    URL: {data['html_url']}")
        else:
            print(f"  FAILED: {resp.status_code} {resp.text}")


if __name__ == "__main__":
    main()
