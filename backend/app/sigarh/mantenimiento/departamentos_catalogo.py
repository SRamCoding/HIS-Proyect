"""Plantilla organizacional editable, basada en CAP MINSA RM 031-2014.
No sustituye el ROF vigente de cada hospital ni constituye exigencia por categoria.
"""
import uuid
from sqlalchemy import select
FUENTE_URL="https://www.minsa.gob.pe/Recursos/normaslegales/2014/RM031_2014_MINSA.pdf"
DEPARTAMENTOS=(
("DEP-MED","Departamento de Medicina"),("DEP-CIR","Departamento de Cirugía"),
("DEP-PED","Departamento de Pediatría"),("DEP-GIN","Departamento de Gineco-Obstetricia"),
("DEP-EME","Departamento de Emergencia y Cuidados Críticos"),
("DEP-ANE","Departamento de Anestesiología y Centro Quirúrgico"),
("DEP-ENF","Departamento de Enfermería"),("DEP-DIA","Departamento de Apoyo al Diagnóstico"),
("DEP-TRA","Departamento de Apoyo al Tratamiento"),("DEP-FAR","Departamento de Farmacia"))
SERVICIO_DEPARTAMENTO={"SRV-MED":"DEP-MED","SRV-CIR":"DEP-CIR","SRV-PED":"DEP-PED","SRV-GIN":"DEP-GIN","SRV-ANE":"DEP-ANE","SRV-EME":"DEP-EME","SRV-UCI":"DEP-EME","SRV-DIA":"DEP-DIA","SRV-REH":"DEP-TRA"}
def departamento_id(tid,code):return uuid.uuid5(uuid.UUID("ab525a19-2e76-442d-a73d-c1dcbde235a8"),str(tid)+":"+code)
async def asegurar_departamentos(db,tid,hospital_level):
 from app.sigarh.mantenimiento.models import Departamento,Servicio
 active=bool(hospital_level and hospital_level.startswith(("II-","III-")))
 deps={}
 for code,name in DEPARTAMENTOS:
  dep=await db.scalar(select(Departamento).where(Departamento.tenant_id==tid,Departamento.codigo==code))
  if not dep:
   dep=Departamento(id=departamento_id(tid,code),tenant_id=tid,codigo=code,nombre=name,is_active=active,descripcion="Plantilla editable basada en CAP MINSA RM 031-2014. Confirmar con ROF institucional. Fuente: "+FUENTE_URL)
   db.add(dep)
  deps[code]=dep.id
 await db.flush()
 for srv in (await db.scalars(select(Servicio).where(Servicio.tenant_id==tid,Servicio.departamento_id.is_(None)))).all():
  if active and srv.codigo in SERVICIO_DEPARTAMENTO:srv.departamento_id=deps[SERVICIO_DEPARTAMENTO[srv.codigo]]
 await db.flush()
