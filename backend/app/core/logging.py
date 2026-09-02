import logging
import sys
from app.core.config import settings


def setup_logging() -> None:
    """
    Configura el logging estructurado con tenant_id.
    En producción esto se conecta a un servicio como Sentry o Datadog.
    """
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )

    # Silenciar logs muy verbosos de SQLAlchemy en producción
    if not settings.DEBUG:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)