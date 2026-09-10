"""merge heads: roles<->programacion medica + config farmacia

Revision ID: b1f4c7a920de
Revises: 4168b3a941c7, 9b7e2a1c4d60
Create Date: 2026-09-09 17:35:00.000000

"""
from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "b1f4c7a920de"
down_revision: Union[str, Sequence[str], None] = ("4168b3a941c7", "9b7e2a1c4d60")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
