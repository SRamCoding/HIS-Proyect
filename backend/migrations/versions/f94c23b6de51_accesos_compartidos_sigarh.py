"""Gestión de cuentas hospitalarias desde roles y perfiles de SIGARH."""
from alembic import op
import sqlalchemy as sa
revision = 'f94c23b6de51'
down_revision = 'e83b12a5cd40'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('sigarh_roles_sistema', sa.Column('tipo_usuario', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('perfil_usuario_id', sa.UUID(), nullable=True))
    op.add_column('users', sa.Column('username', sa.String(100), nullable=True))
    op.create_foreign_key('fk_user_perfil_compartido', 'users', 'sigarh_perfiles_usuario', ['perfil_usuario_id'], ['id'], ondelete='RESTRICT')
    op.create_unique_constraint('uq_user_username', 'users', ['username'])
    # Conserva el perfil anterior con el mismo UUID y todas sus asignaciones.
    op.execute("""INSERT INTO sigarh_roles_sistema (id,tenant_id,codigo,nombre,panel,tipo_usuario,modulos_permitidos,grupos_ocupacionales_permitidos,permisos_accion,alcance_global,is_active,created_at,updated_at)
        SELECT gen_random_uuid(),tenant_id,'HOSP_'||replace(id::text,'-',''),'Hospitalario - '||nombre,'app',role,modulos::text,'[]','[]',false,is_active,now(),now() FROM hospital_perfiles""")
    op.execute("""INSERT INTO sigarh_perfiles_usuario (id,tenant_id,nombre,rol_sistema_id,modulos_acceso,is_active,created_at,updated_at)
        SELECT p.id,p.tenant_id,p.nombre,r.id,p.modulos::text,p.is_active,now(),now() FROM hospital_perfiles p JOIN sigarh_roles_sistema r ON r.codigo='HOSP_'||replace(p.id::text,'-','')""")
    op.execute('UPDATE users SET perfil_usuario_id=perfil_hospital_id WHERE perfil_hospital_id IS NOT NULL')

def downgrade():
    op.drop_constraint('uq_user_username','users',type_='unique')
    op.drop_constraint('fk_user_perfil_compartido','users',type_='foreignkey')
    op.drop_column('users','username')
    op.drop_column('users','perfil_usuario_id')
    op.drop_column('sigarh_roles_sistema','tipo_usuario')
