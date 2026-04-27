import os
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

os.makedirs("data", exist_ok=True)

engine = create_engine(
    settings.database_url,
    # SQLite requires this when shared across threads (FastAPI uses a thread pool)
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def _now() -> datetime:
    # SQLAlchemy column defaults must be callables, not bare values
    return datetime.now(timezone.utc)


class TaskRecord(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    github_issue_number = Column(Integer, unique=True, index=True, nullable=False)
    github_issue_title = Column(String, nullable=False)
    github_issue_url = Column(String, nullable=False)
    github_issue_body = Column(Text, nullable=True)
    devin_session_id = Column(String, nullable=True)
    devin_session_url = Column(String, nullable=True)
    status = Column(String, default="pending", nullable=False)
    pr_url = Column(String, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_now)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db():
    # FastAPI dependency: yields a session and guarantees close on exit
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
