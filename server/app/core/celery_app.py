"""
Celery Configuration
Background task processing for podcast generation
"""
from celery import Celery
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "ai_podcast_generator",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.podcast_tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minutes max per task
    task_soft_time_limit=540,  # 9 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)

# Remove task routing - use default celery queue
# celery_app.conf.task_routes = {
#     "app.tasks.podcast_tasks.generate_podcast_task": {"queue": "podcast_generation"},
# }
