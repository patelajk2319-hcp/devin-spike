import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from app.config import settings

os.makedirs("data", exist_ok=True)

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


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
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
