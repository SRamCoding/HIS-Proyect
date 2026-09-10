"""sigarh_servicios: tiempo_atencion_min (minutos por paciente para cupos)

Revision ID: c2e8d1b3746a
Revises: b1f4c7a920de
Create Date: 2026-09-09 17:36:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c2e8d1b3746a"
down_revision: Union[str, Sequence[str], None] = "b1f4c7a920de"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("sigarh_servicios", sa.Column("tiempo_atencion_min", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("sigarh_servicios", "tiempo_atencion_min")
