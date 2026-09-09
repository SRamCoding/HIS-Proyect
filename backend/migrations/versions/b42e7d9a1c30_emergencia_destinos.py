"""emergencia destinos

Revision ID: b42e7d9a1c30
Revises: a91f3c2d77e0
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b42e7d9a1c30"
down_revision: Union[str, None] = "a91f3c2d77e0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "emergencia_destinos",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("atencion_id", sa.UUID(), nullable=False),
        sa.Column("destino", sa.String(length=30), nullable=False),
        sa.Column("estado", sa.String(length=20), nullable=False),
        sa.Column("observacion", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["atencion_id"], ["atenciones_emergencia.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("atencion_id"),
    )
    op.create_index("ix_emergencia_destinos_tenant_id", "emergencia_destinos", ["tenant_id"])
    op.create_index("ix_emergencia_destinos_destino", "emergencia_destinos", ["destino"])
    op.create_index("ix_emergencia_destinos_estado", "emergencia_destinos", ["estado"])


def downgrade() -> None:
    op.drop_index("ix_emergencia_destinos_estado", table_name="emergencia_destinos")
    op.drop_index("ix_emergencia_destinos_destino", table_name="emergencia_destinos")
    op.drop_index("ix_emergencia_destinos_tenant_id", table_name="emergencia_destinos")
    op.drop_table("emergencia_destinos")
