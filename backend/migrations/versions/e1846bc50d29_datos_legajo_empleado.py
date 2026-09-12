"""Datos de legajo, formacion y contacto del trabajador."""
from alembic import op
import sqlalchemy as sa
revision = "e1846bc50d29"
down_revision = "d06a394f512c"
branch_labels = None
depends_on = None
FIELDS = {'numero_legajo': 50, 'titulo_profesional': 255, 'institucion_formacion': 255, 'documento_vinculo_laboral': 255, 'contacto_emergencia_nombre': 150, 'contacto_emergencia_telefono': 20}

def upgrade():
    for key, length in FIELDS.items():
        op.add_column("sigarh_empleados", sa.Column(key, sa.String(length), nullable=True))
    op.add_column("sigarh_empleados", sa.Column("fecha_titulo", sa.Date(), nullable=True))

def downgrade():
    op.drop_column("sigarh_empleados", "fecha_titulo")
    for key in FIELDS: op.drop_column("sigarh_empleados", key)
