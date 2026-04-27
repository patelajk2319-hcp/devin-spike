import re
from typing import Optional

import httpx

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Compiled once at import time; used to extract PR URLs from Devin's free-text output
_PR_URL_RE = re.compile(r"https://github\.com/[^/]+/[^/]+/pull/\d+")


class DevinService:
    def __init__(self) -> None:
        self.base_url = settings.devin_api_base_url
        self.headers = {
            "Authorization": f"Bearer {settings.devin_api_token}",
            "Content-Type": "application/json",
        }

    def create_session(self, issue_title: str, issue_body: str, issue_url: str) -> dict:
        issue_number = issue_url.split("/")[-1]
        branch_name = f"fix/issue-{issue_number}"
        repo_url = f"https://github.com/{settings.github_repo}.git"
        prompt = (
            f"Fix the following GitHub issue in the repository https://github.com/{settings.github_repo}.\n\n"
            f"Issue #{issue_number}: {issue_title}\n"
            f"URL: {issue_url}\n\n"
            f"Description:\n{issue_body or 'No description provided.'}\n\n"
            f"Instructions — follow these exactly:\n"
            f"1. Clone the repository: git clone {repo_url}\n"
            f"2. Create a new branch: git checkout -b {branch_name}\n"
            f"3. Implement the fix as described in the issue.\n"
            f"4. Commit the changes with a clear message referencing the issue.\n"
            f"5. Push the branch: git push origin {branch_name}\n"
            f"6. Open a pull request from {branch_name} into main with:\n"
            f"   - Title: 'Fix #{issue_number}: {issue_title}'\n"
            f"   - Body: 'Fixes #{issue_number}'\n"
        )
        resp = httpx.post(
            f"{self.base_url}/sessions",
            headers=self.headers,
            json={"prompt": prompt},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        logger.info(f"Created Devin session {data.get('session_id')} for issue {issue_url}")
        return data

    def get_session(self, session_id: str) -> dict:
        resp = httpx.get(
            f"{self.base_url}/session/{session_id}",
            headers=self.headers,
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def send_message(self, session_id: str, message: str) -> dict:
        resp = httpx.post(
            f"{self.base_url}/session/{session_id}/message",
            headers=self.headers,
            json={"message": message},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def extract_pr_url(self, session_data: dict) -> Optional[str]:
        # Prefer structured_output fields; fall back to regex scan of free-text output
        structured = session_data.get("structured_output") or {}
        if isinstance(structured, dict):
            pr = structured.get("pr_url") or structured.get("pull_request_url")
            if pr:
                return pr
        matches = _PR_URL_RE.findall(session_data.get("output") or "")
        return matches[0] if matches else None

    def is_terminal(self, session_data: dict) -> bool:
        return session_data.get("status_enum", "") in {"finished", "stopped", "failed"}

    def is_blocked(self, session_data: dict) -> bool:
        return session_data.get("status_enum") == "blocked"

    def is_success(self, session_data: dict) -> bool:
        return session_data.get("status_enum") == "finished"


devin_service = DevinService()
