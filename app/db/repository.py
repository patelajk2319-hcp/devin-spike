from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.db.database import TaskRecord


def get_task_by_issue(db: Session, issue_number: int) -> Optional[TaskRecord]:
    return db.query(TaskRecord).filter(TaskRecord.github_issue_number == issue_number).first()


def get_task_by_session(db: Session, session_id: str) -> Optional[TaskRecord]:
    return db.query(TaskRecord).filter(TaskRecord.devin_session_id == session_id).first()


def get_all_tasks(db: Session) -> list[TaskRecord]:
    return db.query(TaskRecord).order_by(TaskRecord.created_at.desc()).all()


def get_running_tasks(db: Session) -> list[TaskRecord]:
    # "blocked" tasks are still active — Devin may resume them after a nudge
    return db.query(TaskRecord).filter(TaskRecord.status.in_(["running", "blocked"])).all()


def create_task(
    db: Session,
    issue_number: int,
    issue_title: str,
    issue_url: str,
    issue_body: Optional[str] = None,
) -> TaskRecord:
    record = TaskRecord(
        github_issue_number=issue_number,
        github_issue_title=issue_title,
        github_issue_url=issue_url,
        github_issue_body=issue_body,
        status="pending",
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def update_task(db: Session, task_id: int, **kwargs) -> Optional[TaskRecord]:
    record = db.query(TaskRecord).filter(TaskRecord.id == task_id).first()
    if not record:
        return None
    for key, value in kwargs.items():
        setattr(record, key, value)
    record.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(record)
    return record


def clear_all_tasks(db: Session) -> None:
    db.query(TaskRecord).delete()
    db.commit()


def get_metrics(db: Session) -> dict:
    all_tasks = db.query(TaskRecord).all()
    by_status: dict[str, int] = {}
    for task in all_tasks:
        by_status[task.status] = by_status.get(task.status, 0) + 1
    return {
        "total": len(all_tasks),
        "by_status": by_status,
        "tasks": all_tasks,
    }
