from enum import Enum
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TaskStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class TaskCreate(BaseModel):
    github_issue_number: int
    github_issue_title: str
    github_issue_url: str
    github_issue_body: Optional[str] = None


class TaskRead(BaseModel):
    id: int
    github_issue_number: int
    github_issue_title: str
    github_issue_url: str
    devin_session_id: Optional[str] = None
    devin_session_url: Optional[str] = None
    status: TaskStatus
    pr_url: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
