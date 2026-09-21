"""mfa_totp_en_users

Solo BD central: las cuentas panel="admin" viven exclusivamente en la
tabla `users` central (ver auth/router.py::login, rama admin), nunca en la
BD fisica de un hospital -- no hace falta replicar esto por hospital.

Revision ID: b0fbaf767c28
Revises: 8fabfac480de
Create Date: 2026-09-21 10:41:00.562539

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b0fbaf767c28'
down_revision: Union[str, Sequence[str], None] = '8fabfac480de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('mfa_secret', sa.String(length=64), nullable=True))
    op.add_column('users', sa.Column(
        'mfa_enabled', sa.Boolean(), nullable=False, server_default=sa.false(),
    ))


def downgrade() -> None:
    op.drop_column('users', 'mfa_enabled')
    op.drop_column('users', 'mfa_secret')
