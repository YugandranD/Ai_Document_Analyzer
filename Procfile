web: uvicorn src.main:app --host 0.0.0.0 --port $PORT
worker: celery -A src.celery_worker.celery_app worker --loglevel=info
