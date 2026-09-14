"""Tipos y niveles normativos por profesion."""
import uuid
from alembic import op
import sqlalchemy as sa
from app.sigarh.mantenimiento.escalas_catalogo import TIPOS,PROF_NIVELES,FUENTE_URL,id_catalogo
from app.sigarh.mantenimiento.profesiones_catalogo import PROFESIONES
revision="f25741dc088a"
down_revision="e1846bc50d29"
branch_labels=None
depends_on=None

def upgrade():
 op.add_column("sigarh_tipos_trabajador",sa.Column("vinculos_codigos",sa.JSON(),nullable=True))
 op.add_column("sigarh_niveles_remunerativos",sa.Column("profesion_codigo",sa.String(20),nullable=True))
 op.add_column("sigarh_niveles_remunerativos",sa.Column("fuente_url",sa.Text(),nullable=True))
 bind=op.get_bind()
 tids=set(bind.execute(sa.text("SELECT id FROM tenants")).scalars())
 for table in ("sigarh_usuarios","sigarh_profesiones"):
  tids.update(bind.execute(sa.text("SELECT DISTINCT tenant_id FROM "+table)).scalars())
 names={p[0]:p[1] for p in PROFESIONES}
 import json
 # Ambas tablas tienen un unique index por (tenant_id, nombre) ademas del de
 # codigo; el WHERE NOT EXISTS original solo protegia contra el choque de
 # codigo, asi que un tenant con un tipo de trabajador/nivel homonimo previo
 # (nombre igual, codigo distinto) rompia con un UniqueViolationError en
 # vez de saltarse la fila en silencio.
 for tid in tids:
  for code,name,links in TIPOS:
   bind.execute(sa.text("INSERT INTO sigarh_tipos_trabajador(id,tenant_id,codigo,nombre,descripcion,vinculos_codigos,is_active,created_at,updated_at) SELECT :id,:tid,CAST(:code AS varchar(50)),:name,:description,CAST(:links AS json),true,now(),now() WHERE NOT EXISTS(SELECT 1 FROM sigarh_tipos_trabajador WHERE tenant_id=:tid AND (codigo=CAST(:code AS varchar(50)) OR lower(trim(nombre))=lower(trim(CAST(:name AS varchar(255))))))"),dict(id=id_catalogo(tid,code),tid=tid,code=code,name=name,description="Condicion laboral segun contrato o resolucion",links=json.dumps(links)))
  for prof,levels in PROF_NIVELES.items():
   for level in levels:
    code=prof+"-"+level
    bind.execute(sa.text("INSERT INTO sigarh_niveles_remunerativos(id,tenant_id,codigo,nombre,descripcion,profesion_codigo,fuente_url,is_active,created_at,updated_at) SELECT :id,:tid,CAST(:code AS varchar(50)),:name,:description,:prof,:url,true,now(),now() WHERE NOT EXISTS(SELECT 1 FROM sigarh_niveles_remunerativos WHERE tenant_id=:tid AND (codigo=CAST(:code AS varchar(50)) OR lower(trim(nombre))=lower(trim(CAST(:name AS varchar(255))))))"),dict(id=id_catalogo(tid,code),tid=tid,code=code,name=names[prof]+" - Nivel "+level,description="D.S. 245-2022-EF: identificacion del nivel; verificar plaza y AIRHSP. No fija sueldo vigente.",prof=prof,url=FUENTE_URL))

def downgrade():
 op.drop_column("sigarh_niveles_remunerativos","fuente_url")
 op.drop_column("sigarh_niveles_remunerativos","profesion_codigo")
 op.drop_column("sigarh_tipos_trabajador","vinculos_codigos")
