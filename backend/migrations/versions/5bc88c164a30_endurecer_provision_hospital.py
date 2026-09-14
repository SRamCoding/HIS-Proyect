"""endurecer provision de hospitales

Revision ID: 5bc88c164a30
Revises: dc2b4ceb7cdd
Create Date: 2026-09-11
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "5bc88c164a30"
down_revision: Union[str, Sequence[str], None] = "dc2b4ceb7cdd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("sigarh_usuarios", sa.Column("name", sa.String(255), nullable=True))
    op.execute("""
        DELETE FROM tenant_modules a
        USING tenant_modules b
        WHERE a.tenant_id = b.tenant_id
          AND a.module_code = b.module_code
          AND a.id > b.id
    """)
    op.create_unique_constraint(
        "uq_tenant_module", "tenant_modules", ["tenant_id", "module_code"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_tenant_module", "tenant_modules", type_="unique")
    op.drop_column("sigarh_usuarios", "name")
