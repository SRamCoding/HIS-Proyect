"""preparar importacion CIE-10 MINSA

Revision ID: 8d12f6c37a41
Revises: 5bc88c164a30
Create Date: 2026-09-11
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8d12f6c37a41"
down_revision: Union[str, Sequence[str], None] = "5bc88c164a30"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("sigarh_diagnosticos_cie10", "capitulo", type_=sa.String(255))
    op.alter_column("sigarh_diagnosticos_cie10", "grupo", type_=sa.String(255))
    op.alter_column("sigarh_diagnosticos_cie10", "categoria", type_=sa.String(255))
    op.create_unique_constraint(
        "uq_cie10_tenant_codigo",
        "sigarh_diagnosticos_cie10",
        ["tenant_id", "codigo_cie10"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_cie10_tenant_codigo", "sigarh_diagnosticos_cie10", type_="unique"
    )
    op.alter_column("sigarh_diagnosticos_cie10", "categoria", type_=sa.String(100))
    op.alter_column("sigarh_diagnosticos_cie10", "grupo", type_=sa.String(100))
    op.alter_column("sigarh_diagnosticos_cie10", "capitulo", type_=sa.String(100))
