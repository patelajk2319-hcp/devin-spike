"""Background poller: checks Devin session status for all running tasks
and finalises them when they reach a terminal state."""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.db import repository
from app.db.database import SessionLocal, init_db
from app.services import task_service
from app.services.devin_service import devin_service
from app.utils.logger import get_logger

logger = get_logger("poller")


def poll_once() -> None:
    db = SessionLocal()
    try:
        running = repository.get_running_tasks(db)
        if not running:
            logger.info("No running tasks to poll")
            return

        logger.info(f"Polling {len(running)} running task(s)")
        for task in running:
            try:
                session_data = devin_service.get_session(task.devin_session_id)
                status = session_data.get("status_enum", "unknown")
                logger.info(f"Task id={task.id} session={task.devin_session_id} status={status}")

                if devin_service.is_blocked(session_data):
                    # Update DB first so a crash before send_message doesn't leave status stale
                    logger.info(f"Task id={task.id} is blocked — nudging and marking blocked")
                    repository.update_task(db, task.id, status="blocked")
                    devin_service.send_message(
                        task.devin_session_id,
                        "Please continue. Complete the task, push the branch, and open a pull request.",
                    )
                elif devin_service.is_terminal(session_data):
                    task_service.finalize_task(db, task, session_data)
            except Exception as exc:
                logger.error(f"Error polling task id={task.id}: {exc}")
    finally:
        db.close()


def main() -> None:
    init_db()
    logger.info(f"Poller started (interval={settings.poll_interval_seconds}s)")
    logger.info("ready")
    while True:
        poll_once()
        time.sleep(settings.poll_interval_seconds)


if __name__ == "__main__":
    main()
