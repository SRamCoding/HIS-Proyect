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
    beat_schedule={
        # Red de seguridad para el fallback de auditoria (app/core/audit.py):
        # el fallo normalmente ya dispara un reintento inmediato al ocurrir,
        # pero si ESE encolado tambien fallo (o el proceso se reinicio antes
        # de que corriera), esto lo vuelve a intentar sin depender de que
        # pase nada mas.
        "reintentar-auditoria-fallback": {
            "task": "workers.tasks.reintentar_auditoria_fallback",
            "schedule": 300.0,
        },
        # Red de seguridad para el aprovisionamiento de hospitales: detecta
        # los que quedaron en "pendiente" sin ninguna tarea real corriendo
        # (el proceso murio entre confirmar "pendiente" y encolar la tarea,
        # o el worker que la tomo murio a mitad de camino) y los pasa a
        # "error" para que se puedan reintentar. El umbral de "atascado" es
        # bastante mayor a lo que tarda un aprovisionamiento normal (ver
        # UMBRAL_APROVISIONAMIENTO_ATASCADO), asi que correr esto cada 10
        # minutos es sobrado sin arriesgar falsos positivos.
        "revisar-aprovisionamientos-atascados": {
            "task": "workers.tasks.revisar_aprovisionamientos_atascados",
            "schedule": 600.0,
        },
        # Retencion de notificaciones: la tabla no tenia ningun mecanismo de
        # purga y crecia para siempre. Una vez al dia alcanza de sobra --
        # solo borra leidas con mas de 90 dias, nunca no leidas.
        "purgar-notificaciones-antiguas": {
            "task": "workers.tasks.purgar_notificaciones_antiguas",
            "schedule": 86400.0,
        },
    },
)
