import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.sigarh.infraestructura_hosp.models import Piso, Sala, Cama
from app.hospital.admision.models import Patient
from app.hospital.consulta_externa.models import Hospitalizacion, AtencionMedica, Cita


async def get_pisos(db: AsyncSession, tenant_id: uuid.UUID) -> list[Piso]:
    result = await db.execute(
        select(Piso).where(Piso.tenant_id == tenant_id, Piso.is_active == True).order_by(Piso.orden)
    )
    return result.scalars().all()


async def get_panel_camas(db: AsyncSession, tenant_id: uuid.UUID, piso_id: uuid.UUID | None = None) -> list[dict]:
    query = select(Cama).where(Cama.tenant_id == tenant_id, Cama.is_active == True)
    if piso_id:
        query = query.where(Cama.piso_id == piso_id)
    result = await db.execute(query.order_by(Cama.codigo))
    camas = result.scalars().all()

    items = []
    for cama in camas:
        item = {
            "id": cama.id, "codigo": cama.codigo, "nombre": cama.nombre, "tipo_cama": cama.tipo_cama,
            "estado": cama.estado, "sala_nombre": cama.sala_texto, "servicio_nombre": cama.servicio_texto,
            "paciente_nombre": None, "paciente_dni": None, "fecha_ingreso": None,
            "numero_hospitalizacion": None, "hospitalizacion_cita_id": None,
        }
        if cama.estado == "OCUPADA":
            hosp_result = await db.execute(
                select(Hospitalizacion, AtencionMedica, Cita, Patient)
                .join(AtencionMedica, AtencionMedica.id == Hospitalizacion.atencion_medica_id)
                .join(Cita, Cita.id == AtencionMedica.cita_id)
                .join(Patient, Patient.id == Cita.patient_id)
                .where(Hospitalizacion.cama_id == cama.id, Hospitalizacion.estado == "internado")
            )
            row = hosp_result.first()
            if row:
                hosp, atencion, cita, paciente = row
                item["paciente_nombre"] = paciente.full_name
                item["paciente_dni"] = paciente.dni
                item["fecha_ingreso"] = hosp.fecha_ingreso
                item["numero_hospitalizacion"] = hosp.numero_hospitalizacion
                item["hospitalizacion_cita_id"] = cita.id
        items.append(item)
    return items