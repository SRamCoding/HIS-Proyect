"""Actualiza permisos del administrador SIGARH provisionado sin acciones."""
import json
from alembic import op
import sqlalchemy as sa
revision = "c174a02f993b"
down_revision = "9b6e3a721c44"
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    rows = bind.execute(sa.text("SELECT id, permisos_accion FROM sigarh_roles_sistema WHERE nombre='Administrador SIGARH' AND panel='sigarh' AND alcance_global=true")).all()
    for rid, actions in rows:
        if isinstance(actions, str):
            actions = json.loads(actions)
        if actions == []:
            bind.execute(sa.text("UPDATE sigarh_roles_sistema SET permisos_accion=:actions WHERE id=:id"), {"id": rid, "actions": json.dumps(["administrar_mantenimiento", "administrar_seguridad", "aprobar_roles_turno"])})

def downgrade():
    # No revoca autorizaciones de cuentas existentes.
    pass
