from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List

from app.db.database import TaskRecord


def get_task_by_issue(db: Session, issue_number: int) -> Optional[TaskRecord]:
    return db.query(TaskRecord).filter(TaskRecord.github_issue_number == issue_number).first()


def get_task_by_session(db: Session, session_id: str) -> Optional[TaskRecord]:
    return db.query(TaskRecord).filter(TaskRecord.devin_session_id == session_id).first()


def get_all_tasks(db: Session) -> List[TaskRecord]:
    return db.query(TaskRecord).order_by(TaskRecord.created_at.desc()).all()


def get_running_tasks(db: Session) -> List[TaskRecord]:
    return db.query(TaskRecord).filter(TaskRecord.status == "running").all()


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
    record.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(record)
    return record


def clear_all_tasks(db: Session):
    db.query(TaskRecord).delete()
    db.commit()


def get_metrics(db: Session) -> dict:
    all_tasks = db.query(TaskRecord).all()
    status_counts = {}
    for task in all_tasks:
        status_counts[task.status] = status_counts.get(task.status, 0) + 1
    return {
        "total": len(all_tasks),
        "by_status": status_counts,
        "tasks": all_tasks,
    }
