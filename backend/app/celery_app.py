import os
from celery import Celery
from celery.schedules import crontab

# Initialize Celery targeting a Redis broker container
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery("production_tasks", broker=REDIS_URL, backend=REDIS_URL)

# Configure Celery parameters
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
)

# Automated Task Schedule configuration
celery_app.conf.beat_schedule = {
    "run-data-automation-every-hour": {
        "task": "app.celery_app.automated_report.task",
        "schedule": crontab(minute=0),  # Runs exactly at the top of every hour
    },
}


@celery_app.task
def automated_report_task():
    """Celery wrapper executing the underlying processing script logic."""
    from tasks.data_automation import automate_monthly_report

    print("🚀 Celery Worker:  Initializing automated data execution script...")
    automate_monthly_report()
