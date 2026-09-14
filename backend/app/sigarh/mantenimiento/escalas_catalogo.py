"""Niveles identificados en D.S. 245-2022-EF; no contiene importes salariales."""
import uuid,json
from sqlalchemy import select
NAMESPACE=uuid.UUID("937bbdc2-36cb-40a8-81fe-702043fbf818")
FUENTE_URL="https://busquedas.elperuano.pe/dispositivo/NL/2120504-2"
TIPOS=(("TT-NOMBRADO","Nombrado",["276_NOMBRADO"]),("TT-CONTRATADO","Contratado",["276_CONTRATADO","728_CONTRATADO"]),("TT-CAS","Contratado CAS",["1057_CONTRATADO"]))
PROF_NIVELES={
 "MED":("1","2","3","4","5"),"ENF":("10","11","12","13","14"),
 "ODO":("I","II","III","IV","V"),"OBS":("I","II","III","IV","V"),
 "TME":("1","2","3","4","5"),"TES":("I","II","III","IV","V"),
 **{p:("IV","V","VI","VII","VIII") for p in ("QFA","ISA","VET","BIO","PSI","NUT","TSO","QMC")},
 **{p:tuple(prefix+suffix for prefix in ("SP","ST","SA") for suffix in "ABCDEF") for p in ("TAS","AAS")},
}

def id_catalogo(tid,code): return uuid.uuid5(NAMESPACE,str(tid)+":"+code)

async def asegurar_escalas(db,tid):
 from app.sigarh.mantenimiento.models import TipoTrabajador,NivelRemunerativo
 from app.sigarh.mantenimiento.profesiones_catalogo import PROFESIONES
 nombres={p[0]:p[1] for p in PROFESIONES}
 for code,name,links in TIPOS:
  if not await db.scalar(select(TipoTrabajador.id).where(TipoTrabajador.tenant_id==tid,TipoTrabajador.codigo==code)):
   db.add(TipoTrabajador(id=id_catalogo(tid,code),tenant_id=tid,codigo=code,nombre=name,descripcion="Condicion laboral; verificar contrato o resolucion.",vinculos_codigos=links,is_active=True))
 for prof,levels in PROF_NIVELES.items():
  for level in levels:
   code=prof+"-"+level
   if not await db.scalar(select(NivelRemunerativo.id).where(NivelRemunerativo.tenant_id==tid,NivelRemunerativo.codigo==code)):
    db.add(NivelRemunerativo(id=id_catalogo(tid,code),tenant_id=tid,codigo=code,nombre=nombres[prof]+" - Nivel "+level,descripcion="Nivel identificado en D.S. 245-2022-EF. No fija remuneracion vigente; verificar plaza y AIRHSP.",profesion_codigo=prof,fuente_url=FUENTE_URL,is_active=True))
 await db.flush()
