"""permiso real de aprobación de roles de turno: RolSistema.permisos_accion/
alcance_global, Empleado.es_jefe_servicio, FK de sigarh_usuarios.empleado_id

Revision ID: a3c5e8f1d92b
Revises: bfbf93125c47
Create Date: 2026-09-10 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a3c5e8f1d92b"
down_revision: Union[str, Sequence[str], None] = "bfbf93125c47"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "sigarh_empleados",
        sa.Column("es_jefe_servicio", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column("sigarh_roles_sistema", sa.Column("permisos_accion", sa.Text(), nullable=True))
    op.add_column(
        "sigarh_roles_sistema",
        sa.Column("alcance_global", sa.Boolean(), nullable=False, server_default="false"),
    )

    # Los permisos se asignan explícitamente por Administración ERP.

    # sigarh_usuarios.empleado_id nunca tuvo FK; limpiar referencias huérfanas
    # antes de exigir integridad para no romper el despliegue.
    op.execute("""
        UPDATE sigarh_usuarios u
        SET empleado_id = NULL
        WHERE u.empleado_id IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM sigarh_empleados e WHERE e.id = u.empleado_id)
    """)
    op.create_foreign_key(
        "fk_usuario_sigarh_empleado", "sigarh_usuarios", "sigarh_empleados",
        ["empleado_id"], ["id"], ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_usuario_sigarh_empleado", "sigarh_usuarios", type_="foreignkey")
    op.drop_column("sigarh_roles_sistema", "alcance_global")
    op.drop_column("sigarh_roles_sistema", "permisos_accion")
    op.drop_column("sigarh_empleados", "es_jefe_servicio")
