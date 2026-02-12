"""Celery application configuration."""
from celery import Celery
from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "job_search_worker",
    broker=settings.redis_url,
    backend=settings.redis_url.replace("/0", "/1"),
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    task_time_limit=3600,           # 1 hour hard limit
    task_soft_time_limit=3000,      # 50 min soft limit
    worker_prefetch_multiplier=1,   # One task at a time (heavy)
    worker_concurrency=2,           # 2 concurrent scrapes per worker
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.tasks"])
