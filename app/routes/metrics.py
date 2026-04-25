from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.db import repository
from app.models.task import TaskRead

router = APIRouter()


@router.get("/metrics")
def get_metrics(db: Session = Depends(get_db)):
    data = repository.get_metrics(db)
    return {
        "total": data["total"],
        "by_status": data["by_status"],
    }


@router.get("/tasks", response_model=List[TaskRead])
def list_tasks(db: Session = Depends(get_db)):
    return repository.get_all_tasks(db)


@router.get("/tasks/{task_id}", response_model=TaskRead)
def get_task(task_id: int, db: Session = Depends(get_db)):
    from app.db.database import TaskRecord
    task = db.query(TaskRecord).filter(TaskRecord.id == task_id).first()
    if not task:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("/health")
def health():
    return {"status": "ok"}
