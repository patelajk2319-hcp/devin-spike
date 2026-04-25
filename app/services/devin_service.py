import httpx
from typing import Optional

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DevinService:
    def __init__(self):
        self.base_url = settings.devin_api_base_url
        self.headers = {
            "Authorization": f"Bearer {settings.devin_api_token}",
            "Content-Type": "application/json",
        }

    def create_session(self, issue_title: str, issue_body: str, issue_url: str) -> dict:
        prompt = (
            f"You are fixing a GitHub issue in the repository {settings.github_repo}.\n\n"
            f"Issue: {issue_title}\nURL: {issue_url}\n\n"
            f"Description:\n{issue_body or 'No description provided.'}\n\n"
            f"Steps:\n"
            f"1. Clone the repository if not already available.\n"
            f"2. Understand the issue and implement the fix.\n"
            f"3. Write or update tests if appropriate.\n"
            f"4. Open a pull request with a clear title referencing the issue.\n"
            f"5. Include 'Fixes #{issue_url.split('/')[-1]}' in the PR body.\n"
        )
        payload = {"prompt": prompt}
        resp = httpx.post(
            f"{self.base_url}/sessions",
            headers=self.headers,
            json=payload,
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
        """Pull PR URL out of Devin session structured_output or status_enum."""
        structured = session_data.get("structured_output") or {}
        if isinstance(structured, dict):
            pr = structured.get("pr_url") or structured.get("pull_request_url")
            if pr:
                return pr

        # Fall back: scan plain-text output for a GitHub PR URL
        output = session_data.get("output") or ""
        import re
        matches = re.findall(
            r"https://github\.com/[^/]+/[^/]+/pull/\d+", output
        )
        return matches[0] if matches else None

    def is_terminal(self, session_data: dict) -> bool:
        status = session_data.get("status_enum", "")
        return status in {"finished", "stopped", "failed", "blocked"}

    def is_success(self, session_data: dict) -> bool:
        return session_data.get("status_enum") == "finished"


devin_service = DevinService()
