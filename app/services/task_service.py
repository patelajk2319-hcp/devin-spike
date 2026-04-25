from sqlalchemy.orm import Session

from app.db import repository
from app.services.devin_service import devin_service
from app.services.github_service import github_service
from app.utils.logger import get_logger

logger = get_logger(__name__)


def handle_labeled_issue(
    db: Session,
    issue_number: int,
    issue_title: str,
    issue_url: str,
    issue_body: str,
):
    existing = repository.get_task_by_issue(db, issue_number)
    if existing:
        logger.info(f"Issue #{issue_number} already tracked (status={existing.status}), skipping")
        return existing

    task = repository.create_task(
        db,
        issue_number=issue_number,
        issue_title=issue_title,
        issue_url=issue_url,
        issue_body=issue_body,
    )
    logger.info(f"Created task id={task.id} for issue #{issue_number}")

    try:
        session_data = devin_service.create_session(issue_title, issue_body or "", issue_url)
        session_id = session_data["session_id"]
        session_url = session_data.get("url") or f"https://app.devin.ai/sessions/{session_id}"

        task = repository.update_task(
            db,
            task.id,
            devin_session_id=session_id,
            devin_session_url=session_url,
            status="running",
        )
        logger.info(f"Devin session {session_id} started for task id={task.id}")
        github_service.comment_session_started(issue_number, session_url)
    except Exception as exc:
        logger.error(f"Failed to start Devin session for issue #{issue_number}: {exc}")
        repository.update_task(db, task.id, status="failed", error=str(exc))
        raise

    return task


def finalize_task(db: Session, task_record, session_data: dict):
    session_url = task_record.devin_session_url or f"https://app.devin.ai/sessions/{task_record.devin_session_id}"

    if devin_service.is_success(session_data):
        pr_url = devin_service.extract_pr_url(session_data)
        repository.update_task(
            db,
            task_record.id,
            status="completed",
            pr_url=pr_url,
        )
        logger.info(f"Task id={task_record.id} completed. PR={pr_url}")
        github_service.comment_session_completed(
            task_record.github_issue_number, pr_url, session_url
        )
    else:
        status_enum = session_data.get("status_enum", "unknown")
        error = f"Devin session ended with status: {status_enum}"
        repository.update_task(db, task_record.id, status="failed", error=error)
        logger.warning(f"Task id={task_record.id} failed: {error}")
        github_service.comment_session_failed(
            task_record.github_issue_number, session_url, error
        )
