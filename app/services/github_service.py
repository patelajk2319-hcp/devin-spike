from typing import Optional

import httpx

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

_BASE = "https://api.github.com"
_HEADERS_TEMPLATE = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


class GitHubService:
    def __init__(self) -> None:
        self.headers = {
            **_HEADERS_TEMPLATE,
            "Authorization": f"Bearer {settings.github_token}",
        }
        self.repo = settings.github_repo

    def post_comment(self, issue_number: int, body: str) -> None:
        url = f"{_BASE}/repos/{self.repo}/issues/{issue_number}/comments"
        resp = httpx.post(url, headers=self.headers, json={"body": body}, timeout=15)
        resp.raise_for_status()
        logger.info(f"Posted comment on issue #{issue_number}")

    def add_label(self, issue_number: int, label: str) -> None:
        url = f"{_BASE}/repos/{self.repo}/issues/{issue_number}/labels"
        resp = httpx.post(url, headers=self.headers, json={"labels": [label]}, timeout=15)
        resp.raise_for_status()

    def remove_label(self, issue_number: int, label: str) -> None:
        url = f"{_BASE}/repos/{self.repo}/issues/{issue_number}/labels/{label}"
        resp = httpx.delete(url, headers=self.headers, timeout=15)
        # 404 is fine — label was already absent
        if resp.status_code not in (200, 204, 404):
            resp.raise_for_status()

    def comment_session_started(self, issue_number: int, session_url: str) -> None:
        body = (
            "## Devin Remediation Started\n\n"
            f"A Devin session has been created to address this issue.\n\n"
            f"**Session:** {session_url}\n\n"
            "_This comment will be updated when the session completes._"
        )
        self.post_comment(issue_number, body)

    def comment_session_completed(
        self, issue_number: int, pr_url: Optional[str], session_url: str
    ) -> None:
        if pr_url:
            body = (
                "## Devin Remediation Completed\n\n"
                f"Devin has finished working on this issue.\n\n"
                f"**Pull Request:** {pr_url}\n"
                f"**Session:** {session_url}"
            )
        else:
            body = (
                "## Devin Remediation Completed\n\n"
                f"Devin finished the session but no PR URL was detected.\n\n"
                f"**Session:** {session_url}\n\n"
                "_Please review the session output manually._"
            )
        self.post_comment(issue_number, body)

    def comment_session_failed(
        self, issue_number: int, session_url: str, error: Optional[str] = None
    ) -> None:
        body = (
            "## Devin Remediation Failed\n\n"
            f"The Devin session ended without successfully completing the fix.\n\n"
            f"**Session:** {session_url}\n"
        )
        if error:
            body += f"\n**Details:** {error}"
        self.post_comment(issue_number, body)


github_service = GitHubService()
