"""programaciones_medicas: codigo correlativo, modalidad, consultorio_id

Revision ID: d4a91f6c2b70
Revises: c2e8d1b3746a
Create Date: 2026-09-10 09:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d4a91f6c2b70"
down_revision: Union[str, Sequence[str], None] = "c2e8d1b3746a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SEQUENCE IF NOT EXISTS programacion_medica_codigo_seq START 1")

    op.add_column("programaciones_medicas", sa.Column("codigo", sa.String(20), nullable=True))
    op.add_column("programaciones_medicas", sa.Column(
        "modalidad", sa.String(20), nullable=False, server_default="PRESENCIAL"))
    op.add_column("programaciones_medicas", sa.Column("consultorio_id", sa.UUID(), nullable=True))
    op.create_foreign_key(
        "fk_programacion_consultorio", "programaciones_medicas", "sigarh_consultorios",
        ["consultorio_id"], ["id"], ondelete="SET NULL",
    )

    # Backfill de correlativos para filas existentes (orden por antigüedad).
    op.execute("""
        UPDATE programaciones_medicas p
        SET codigo = seq.n::text
        FROM (
            SELECT id, nextval('programacion_medica_codigo_seq') AS n
            FROM programaciones_medicas
            WHERE codigo IS NULL
            ORDER BY created_at, id
        ) seq
        WHERE p.id = seq.id
    """)

    op.alter_column(
        "programaciones_medicas", "codigo", nullable=False,
        server_default=sa.text("nextval('programacion_medica_codigo_seq')::text"),
    )
    op.create_index("ix_programaciones_medicas_codigo", "programaciones_medicas", ["codigo"])


def downgrade() -> None:
    op.drop_index("ix_programaciones_medicas_codigo", table_name="programaciones_medicas")
    op.drop_constraint("fk_programacion_consultorio", "programaciones_medicas", type_="foreignkey")
    op.drop_column("programaciones_medicas", "consultorio_id")
    op.drop_column("programaciones_medicas", "modalidad")
    op.drop_column("programaciones_medicas", "codigo")
    op.execute("DROP SEQUENCE IF EXISTS programacion_medica_codigo_seq")
