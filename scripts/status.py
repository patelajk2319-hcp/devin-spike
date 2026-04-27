"""Prints a summary table of all tasks in the database.
Run: python scripts/status.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal, init_db
from app.db.repository import get_all_tasks

_WIDTH = 110

init_db()
db = SessionLocal()
tasks = get_all_tasks(db)
db.close()

if not tasks:
    print("No tasks in database")
else:
    separator = "-" * _WIDTH
    print(separator)
    print(f'{"ID":<4} {"ISSUE":<6} {"STATUS":<12} {"TITLE":<35} {"PR / ERROR"}')
    print(separator)
    for t in tasks:
        title = t.github_issue_title[:33] + ".." if len(t.github_issue_title) > 35 else t.github_issue_title
        detail = (
            t.pr_url
            or (t.error[:60] + ".." if t.error and len(t.error) > 60 else t.error)
            or "-"
        )
        print(f"{t.id:<4} #{t.github_issue_number:<5} {t.status:<12} {title:<35} {detail}")
    print(separator)
