"""integrar roles SIGARH programacion medica

Revision ID: 9b7e2a1c4d60
Revises: 74c49570f1f9
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "9b7e2a1c4d60"
down_revision: Union[str, Sequence[str], None] = "74c49570f1f9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "programaciones_medicas",
        sa.Column("origen_sigarh_turno_id", sa.UUID(), nullable=True),
    )
    op.create_foreign_key(
        "fk_programacion_sigarh_turno",
        "programaciones_medicas",
        "sigarh_roles_turno_turnos",
        ["origen_sigarh_turno_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_programaciones_medicas_origen_sigarh_turno_id",
        "programaciones_medicas",
        ["origen_sigarh_turno_id"],
        unique=False,
    )
    op.create_unique_constraint(
        "uq_programacion_sigarh_turno_fecha",
        "programaciones_medicas",
        ["tenant_id", "origen_sigarh_turno_id", "fecha"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_programacion_sigarh_turno_fecha", "programaciones_medicas", type_="unique")
    op.drop_index("ix_programaciones_medicas_origen_sigarh_turno_id", table_name="programaciones_medicas")
    op.drop_constraint("fk_programacion_sigarh_turno", "programaciones_medicas", type_="foreignkey")
    op.drop_column("programaciones_medicas", "origen_sigarh_turno_id")
