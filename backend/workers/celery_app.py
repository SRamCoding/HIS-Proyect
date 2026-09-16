# backend/workers/celery_app.py
"""App de Celery para trabajo pesado en segundo plano (aprovisionar un
hospital). El paquete `celery` y los contenedores de Redis/RabbitMQ ya
estaban en el proyecto (pyproject.toml, infra/docker-compose.yml) -- este
archivo era la pieza que faltaba, el servicio `celery -A workers.celery_app
worker` del compose apuntaba a un modulo que no existia todavia.

Correr el worker (aparte de uvicorn):
    celery -A workers.celery_app worker --loglevel=info
"""
from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "erp_hospitalario",
    broker=settings.RABBITMQ_URL,
    backend=settings.REDIS_URL,
    include=["workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Lima",
    enable_utc=True,
    task_track_started=True,
)
