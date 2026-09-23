"""HC por DNI, conservando números anteriores y evidencias firmadas.

Revision ID: d2e3f4a5b6c7
Revises: c1a2b3d4e5f6
"""
from alembic import op
import sqlalchemy as sa

revision = "d2e3f4a5b6c7"
down_revision = "c1a2b3d4e5f6"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("clinical_records", "record_number", type_=sa.String(64), existing_type=sa.String(20))
    op.add_column("clinical_records", sa.Column("previous_record_numbers", sa.JSON(), nullable=False, server_default="[]"))
    conn = op.get_bind()
    # La restricción única existente aborta toda la migración ante colisiones;
    # nunca reasignar silenciosamente una historia a otro paciente.
    conn.execute(sa.text("""
        UPDATE clinical_records AS r
        SET previous_record_numbers = json_build_array(r.record_number), record_number = p.dni
        FROM patients AS p
        WHERE r.patient_id = p.id AND p.document_type = 'DNI'
          AND NOT p.is_nn AND p.dni ~ '^[0-9]{8}$' AND r.record_number <> p.dni
    """))


def downgrade():
    raise RuntimeError(
        "La numeración clínica y sus alias no se eliminan automáticamente. "
        "Restaure un respaldo verificado para revertir esta migración."
    )
