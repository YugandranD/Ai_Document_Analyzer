"""
Celery worker for asynchronous document processing.
Uses Redis as the message broker.
"""

from celery import Celery
from src.config import REDIS_URL

celery_app = Celery(
    "document_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 min max per task
    task_soft_time_limit=240,
)


@celery_app.task(name="process_document", bind=True, max_retries=2)
def process_document_task(self, file_name: str, file_type: str, file_base64: str):
    """
    Async Celery task that extracts text and runs AI analysis.
    """
    from src.extractors import decode_base64, extract_text
    from src.analyzer import analyze_document

    try:
        file_bytes = decode_base64(file_base64)
        extracted_text = extract_text(file_type, file_bytes)
        analysis = analyze_document(extracted_text)

        return {
            "status": "success",
            "fileName": file_name,
            "summary": analysis["summary"],
            "entities": analysis["entities"],
            "sentiment": analysis["sentiment"],
        }
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)
