import hashlib
import hmac

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.config import settings
from app.db.database import get_db
from app.services import task_service
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


def _verify_signature(payload: bytes, signature_header: str | None) -> None:
    # compare_digest prevents timing-based signature oracle attacks
    if not signature_header:
        raise HTTPException(status_code=401, detail="Missing X-Hub-Signature-256")
    secret = settings.github_webhook_secret.encode()
    expected = "sha256=" + hmac.new(secret, payload, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature_header):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")


@router.post("/webhook")
async def github_webhook(request: Request, db: Session = Depends(get_db)):
    payload_bytes = await request.body()
    _verify_signature(payload_bytes, request.headers.get("X-Hub-Signature-256"))

    event = request.headers.get("X-GitHub-Event", "")
    if event != "issues":
        return {"ignored": True, "reason": f"event '{event}' not handled"}

    body = await request.json()
    action = body.get("action", "")

    if action not in ("labeled", "reopened"):
        return {"ignored": True, "reason": f"action '{action}' not handled"}

    label_name = (body.get("label") or {}).get("name", "")
    if label_name != settings.remediation_label:
        return {"ignored": True, "reason": f"label '{label_name}' not monitored"}

    issue = body["issue"]
    issue_number: int = issue["number"]
    issue_title: str = issue["title"]
    issue_url: str = issue["html_url"]
    issue_body: str = issue.get("body") or ""

    logger.info(f"Webhook: issue #{issue_number} labeled '{label_name}'")

    task = task_service.handle_labeled_issue(
        db=db,
        issue_number=issue_number,
        issue_title=issue_title,
        issue_url=issue_url,
        issue_body=issue_body,
    )

    return {"accepted": True, "task_id": task.id, "issue": issue_number}
