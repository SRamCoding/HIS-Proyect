"""Verifica la cita existente y prueba confirmacion con rollback completo."""
import asyncio
import json
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import engine
from app.core.tenant_db import get_tenant_sessionmaker, _tenant_engines
import app.shared.ubigeo.models
from app.hospital.consulta_externa import service
from app.hospital.consulta_externa.schemas import CitaUpdate

TID = uuid.UUID("55540838-24a6-4e78-843b-f9b93e57733a")

async def main():
    get_tenant_sessionmaker("his_hospital_reque")
    try:
        async with _tenant_engines["his_hospital_reque"].connect() as conn:
            tx = await conn.begin()
            try:
                async with AsyncSession(bind=conn, expire_on_commit=False, join_transaction_mode="create_savepoint") as db:
                    citas = await service.list_citas(db, TID)
                    print(json.dumps({"citas": [{"id": str(c["id"]), "fecha": str(c["fecha"]), "estado": c["estado"]} for c in citas]}))
                    separadas = [c for c in citas if c["estado"] == "separada"]
                    assert separadas, "No hay cita separada para probar"
                    cita = separadas[0]
                    for estado in ("atendida", "confirmada", "no_asistio"):
                        try:
                            await service.update_cita(db, TID, cita["id"], CitaUpdate(estado=estado))
                        except ValueError:
                            print("bloqueo_" + estado + ": OK")
                        else:
                            raise AssertionError("Transicion incorrecta: " + estado)
                    assert await service.confirmar_cita(db, uuid.uuid4(), cita["id"]) is None
                    result = await service.confirmar_cita(db, TID, cita["id"])
                    assert result["estado"] == "confirmada"
                    pendientes = await service.list_citas_para_triaje(db, TID, fecha=cita["fecha"])
                    assert any(c["cita_id"] == cita["id"] for c in pendientes)
                    print("confirmacion_y_triaje: OK")
                    try:
                        await service.confirmar_cita(db, TID, cita["id"])
                    except ValueError:
                        print("doble_confirmacion: bloqueada")
                    else:
                        raise AssertionError("Doble confirmacion permitida")
            finally:
                await tx.rollback()
        async with get_tenant_sessionmaker("his_hospital_reque")() as db:
            original = await service.get_cita_by_id(db, TID, cita["id"])
            assert original["estado"] == "separada"
            print("rollback: cita original preservada")
    finally:
        await engine.dispose()
        for tenant_engine in _tenant_engines.values():
            await tenant_engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
