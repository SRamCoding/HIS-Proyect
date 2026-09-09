"""Prueba temporal del circuito firma -> destino; restaura el registro usado."""
import asyncio
from sqlalchemy import delete, select, update

import main  # noqa: F401
from app.core.database import AsyncSessionLocal
from app.hospital.emergencia.models import AdmisionEmergencia, AtencionEmergencia, DestinoEmergencia
from app.hospital.emergencia.service import (
    firmar_atencion_emergencia,
    list_destinos_emergencia,
    resolver_destino_emergencia,
)


async def run():
    async with AsyncSessionLocal() as db:
        row = (await db.execute(select(AtencionEmergencia, AdmisionEmergencia).join(
            AdmisionEmergencia, AdmisionEmergencia.id == AtencionEmergencia.admision_id
        ).where(AtencionEmergencia.estado != "firmado").limit(1))).first()
        if not row:
            print("SKIP: no hay borrador")
            return
        a, adm = row
        aid, adid, tid = a.id, adm.id, a.tenant_id
        original = (a.estado, a.firmado_at, a.destino_atencion, adm.estado)
        try:
            a.destino_atencion = "HOSPITALIZACION"
            await db.commit()
            await firmar_atencion_emergencia(db, tid, adid)
            items = await list_destinos_emergencia(db, tid, "HOSPITALIZACION", "pendiente")
            item = next(i for i in items if i["atencion_id"] == aid)
            resolved = await resolver_destino_emergencia(db, tid, item["id"], "Prueba automatizada")
            assert resolved and resolved["estado"] == "completado"
            print("OK: firma -> bandeja HOSPITALIZACION -> completado")
        finally:
            await db.rollback()
            await db.execute(delete(DestinoEmergencia).where(DestinoEmergencia.atencion_id == aid))
            await db.execute(update(AtencionEmergencia).where(AtencionEmergencia.id == aid).values(
                estado=original[0], firmado_at=original[1], destino_atencion=original[2]))
            await db.execute(update(AdmisionEmergencia).where(AdmisionEmergencia.id == adid).values(estado=original[3]))
            await db.commit()


if __name__ == "__main__":
    asyncio.run(run())
