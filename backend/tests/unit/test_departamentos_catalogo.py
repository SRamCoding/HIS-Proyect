from app.sigarh.mantenimiento.departamentos_catalogo import DEPARTAMENTOS,SERVICIO_DEPARTAMENTO,departamento_id
from app.sigarh.mantenimiento.upss_catalogo import SERVICIOS
import uuid

def test_mapping_covers_existing_base_services():
 assert set(SERVICIO_DEPARTAMENTO)=={s[0] for s in SERVICIOS}
 assert set(SERVICIO_DEPARTAMENTO.values()) <= {d[0] for d in DEPARTAMENTOS}

def test_ids_are_stable_and_isolated_by_hospital():
 a,b=uuid.uuid4(),uuid.uuid4()
 assert departamento_id(a,"DEP-MED")==departamento_id(a,"DEP-MED")
 assert departamento_id(a,"DEP-MED")!=departamento_id(b,"DEP-MED")
