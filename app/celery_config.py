from celery import Celery
import logging


# Configure logging for Celery workers
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

celery_app = Celery(
    'RAG Observatory',
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["celery_tasks.tasks"],
)

celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]
