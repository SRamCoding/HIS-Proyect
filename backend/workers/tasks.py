# backend/workers/tasks.py
"""Tareas de Celery. El aprovisionamiento de un hospital es pesado (crea una
BD fisica, la migra, siembra catalogos, crea usuarios) y antes corria atado
a la peticion HTTP de POST /admin/hospitales -- si el cliente se
desconectaba a mitad de camino, el trabajo seguia a ciegas en el worker de
uvicorn. Ahora esa parte se encola aqui y el endpoint responde de inmediato.
"""
import asyncio
import uuid

from workers.celery_app import celery_app


@celery_app.task(name="workers.tasks.aprovisionar_hospital")
def aprovisionar_hospital(
    tenant_id: str,
    database_name: str,
    hospital_level: str,
    active_modules: list[str],
    admin_name: str, admin_email: str, admin_password: str,
    sigarh_name: str, sigarh_email: str, sigarh_password: str,
) -> None:
    from app.tenants.hospitales.service import aprovisionar_hospital_async

    asyncio.run(aprovisionar_hospital_async(
        tenant_id=uuid.UUID(tenant_id),
        database_name=database_name,
        hospital_level=hospital_level,
        active_modules=active_modules,
        admin_name=admin_name, admin_email=admin_email, admin_password=admin_password,
        sigarh_name=sigarh_name, sigarh_email=sigarh_email, sigarh_password=sigarh_password,
    ))
