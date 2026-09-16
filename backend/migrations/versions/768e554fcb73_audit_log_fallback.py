"""audit_log_fallback

Revision ID: 768e554fcb73
Revises: d531c26e6a2c
Create Date: 2026-09-16 11:17:50.780558

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '768e554fcb73'
down_revision: Union[str, Sequence[str], None] = 'd531c26e6a2c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'audit_log_fallback',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('ocurrido_en', sa.DateTime(), nullable=False),
        sa.Column('actor', sa.JSON(), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('entrada', sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('audit_log_fallback')
