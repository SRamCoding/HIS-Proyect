"""Permite completar departamento vacio sin alterar identidad del servicio."""
from alembic import op
import sqlalchemy as sa
revision="0c824b51ab69"
down_revision="f25741dc088a"
branch_labels=None
depends_on=None
GUARD="""IF TG_OP='UPDATE' AND TG_TABLE_NAME='sigarh_servicios' THEN
 IF (to_jsonb(OLD)->>'departamento_id') IS NULL AND (to_jsonb(NEW)->>'departamento_id') IS NOT NULL
 AND (to_jsonb(NEW)-'updated_at'-'departamento_id')=(to_jsonb(OLD)-'updated_at'-'departamento_id') THEN RETURN NEW; END IF;
 END IF;
 """
def upgrade():
 bind=op.get_bind()
 sql=bind.scalar(sa.text("SELECT pg_get_functiondef('mantenimiento_proteger_catalogo()'::regprocedure)"))
 sql=sql.replace("BEGIN", "BEGIN\n"+GUARD,1)
 op.execute(sql)
def downgrade():
 bind=op.get_bind()
 sql=bind.scalar(sa.text("SELECT pg_get_functiondef('mantenimiento_proteger_catalogo()'::regprocedure)"))
 op.execute(sql.replace(GUARD,""))
