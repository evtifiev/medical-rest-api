"""create default table

Revision ID: 1123e430968c
Revises: 
Create Date: 2018-12-06 17:15:26.845697

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1123e430968c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Таблица Должности
    op.create_table(
        'position',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('created', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column('modified', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column('name', sa.String(255), nullable=False, unique=True)
    )
    # Таблица Подразделения
    op.create_table(
        'department',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('created', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column('modified', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column('name', sa.String(255), nullable=False, unique=True)
    )
    # Таблица Модули
    op.create_table(
        'module',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('created', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column('modified', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column('name', sa.String(90), nullable=False),
        sa.Column('parent_id', sa.ForeignKey('module.id', ondelete='CASCADE')),
        sa.Column('url', sa.String(90), nullable=False)
    )
    # Таблица Разрешение модулей
    op.create_table(
        'module_permission',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('created', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column('modified', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column('module_id', sa.Integer, sa.ForeignKey('module.id', ondelete='CASCADE')),
        sa.Column('name', sa.String(90), nullable=False),
        sa.Column('url', sa.String(90), nullable=False),
        sa.Column('method', sa.String(10), nullable=False)
    )
    # Таблица роли
    op.create_table(
        'role',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('created', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column('modified', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column('name', sa.String(90), nullable=False),
        sa.Column('description', sa.String(255), nullable=False),
        sa.Column('default', sa.Boolean, nullable=False, default=False),
        sa.Column('visible', sa.Boolean, nullable=False, default=True),
        sa.Column('deleted', sa.Boolean, nullable=False, default=False)
    )
    # Таблица Меню
    op.create_table(
        'menu',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('created', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column('modified', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column('name', sa.String(90), nullable=False),
        sa.Column('description', sa.String(255), nullable=False)
    )
    # Таблица связи Роли-Разрешения модулей
    op.create_table(
        'role_has_module_permission',
        sa.Column('role_id', sa.Integer, sa.ForeignKey('role.id', ondelete='CASCADE')),
        sa.Column('module_permission_id', sa.Integer, sa.ForeignKey('module_permission.id', ondelete='CASCADE')),
    )
    # Таблица связи Роли-Разрешения модулей
    op.create_table(
        'menu_has_module',
        sa.Column('menu_id', sa.Integer, sa.ForeignKey('menu.id', ondelete='CASCADE')),
        sa.Column('module_id', sa.Integer, sa.ForeignKey('module.id', ondelete='CASCADE')),
    )
    # Таблица Пользователи
    op.create_table(
        'user',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('created', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column('modified', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column('username', sa.String(60), nullable=False, unique=True),
        sa.Column('password', sa.String(80), nullable=False),
        sa.Column('last_name', sa.String(90), nullable=True),
        sa.Column('first_name', sa.String(40), nullable=True),
        sa.Column('middle_name', sa.String(40), nullable=True),
        sa.Column('email', sa.String(90), nullable=False, unique=True),
        sa.Column('email_password', sa.String(120), nullable=True),
        sa.Column('mobile', sa.String(80), nullable=True),
        sa.Column('phone', sa.String(120), nullable=True),
        sa.Column('info', sa.JSON),
        sa.Column('blocked', sa.Boolean, default=False),
        sa.Column('numeric_id', sa.String(12), nullable=False),
        sa.Column('token', sa.String(255), nullable=False),
        sa.Column('role_id', sa.Integer, sa.ForeignKey('role.id'), nullable=True),
        sa.Column('menu_id', sa.Integer, sa.ForeignKey('menu.id'), nullable=True),
        sa.Column('department_id', sa.Integer, sa.ForeignKey('department.id'), nullable=True),
        sa.Column('position_id', sa.Integer, sa.ForeignKey('position.id'), nullable=True)
    )


def downgrade():
    op.drop_table('position')
    op.drop_table('department')
    op.drop_table('module')
    op.drop_table('module_permission')
    op.drop_table('role')
    op.drop_table('menu')
    op.drop_table('role_has_module_permission')
    op.drop_table('menu_has_module')
    op.drop_table('user')
