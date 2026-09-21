"""cifrar_mfa_secret

Amplia users.mfa_secret (guardaba texto plano en String(64); un token
Fernet cifrado ronda los 140 caracteres) y cifra en el lugar cualquier
secreto ya guardado en texto plano -- solo aplica a la BD central, las
cuentas panel=admin no viven en ninguna BD de hospital.

Revision ID: c1a2b3d4e5f6
Revises: b0fbaf767c28
Create Date: 2026-09-21 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'c1a2b3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'b0fbaf767c28'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('users', 'mfa_secret', type_=sa.String(length=255), existing_type=sa.String(length=64))

    # Cifra cualquier secreto que haya quedado en texto plano de antes de
    # este cambio (un base32 valido de pyotp mide 32 caracteres y solo usa
    # A-Z2-7 -- un token Fernet no calza ese patron, asi que sirve para
    # distinguir "ya esta cifrado" de "todavia esta en claro" sin necesitar
    # una columna aparte).
    from app.core.crypto import cifrar
    import re

    conn = op.get_bind()
    filas = conn.execute(sa.text(
        "SELECT id, mfa_secret FROM users WHERE mfa_secret IS NOT NULL"
    )).fetchall()
    patron_base32 = re.compile(r'^[A-Z2-7]{16,64}$')
    for fila in filas:
        if patron_base32.match(fila.mfa_secret):
            conn.execute(
                sa.text("UPDATE users SET mfa_secret = :nuevo WHERE id = :id"),
                {"nuevo": cifrar(fila.mfa_secret), "id": fila.id},
            )


def downgrade() -> None:
    op.alter_column('users', 'mfa_secret', type_=sa.String(length=64), existing_type=sa.String(length=255))
