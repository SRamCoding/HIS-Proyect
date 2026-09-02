from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """
    Registra todos los handlers globales de error.
    Se llama desde main.py al crear la app.
    """

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "ok": False,
                "status": exc.status_code,
                "message": exc.detail,
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        Errores de validación Pydantic — equivalente a los 422 de Laravel.
        Formatea los errores igual que Laravel: {campo: [mensaje]}
        """
        errors = {}
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
            if field not in errors:
                errors[field] = []
            errors[field].append(error["msg"])

        return JSONResponse(
            status_code=422,
            content={
                "ok": False,
                "status": 422,
                "message": "Error de validación",
                "errors": errors,
            }
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        logger.error(f"Error de base de datos: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "status": 500,
                "message": "Error interno de base de datos",
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Error no controlado: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "status": 500,
                "message": "Error interno del servidor",
            }
        )
    