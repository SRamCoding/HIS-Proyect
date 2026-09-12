"""Regimen y condicion laboral del trabajador."""
from alembic import op
import sqlalchemy as sa
from app.sigarh.rrhh.laboral_catalogo import VINCULOS
revision = "d06a394f512c"
down_revision = "c174a02f993b"
branch_labels = None
depends_on = None

def upgrade():
    table = op.create_table("catalogo_vinculos_laborales",
        sa.Column("codigo", sa.String(30), primary_key=True),
        sa.Column("regimen_codigo", sa.String(10), nullable=False),
        sa.Column("regimen_nombre", sa.String(150), nullable=False),
        sa.Column("condicion_nombre", sa.String(100), nullable=False),
        sa.Column("norma", sa.String(255), nullable=False),
        sa.Column("fuente_url", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()))
    keys = ("codigo", "regimen_codigo", "regimen_nombre", "condicion_nombre", "norma", "fuente_url")
    op.bulk_insert(table, [dict(zip(keys, row), is_active=True) for row in VINCULOS])
    op.add_column("sigarh_empleados", sa.Column("vinculo_laboral_codigo", sa.String(30), nullable=True))
    op.create_foreign_key("fk_empleado_vinculo_laboral", "sigarh_empleados", "catalogo_vinculos_laborales", ["vinculo_laboral_codigo"], ["codigo"], ondelete="RESTRICT")

def downgrade():
    op.drop_constraint("fk_empleado_vinculo_laboral", "sigarh_empleados", type_="foreignkey")
    op.drop_column("sigarh_empleados", "vinculo_laboral_codigo")
    op.drop_table("catalogo_vinculos_laborales")
