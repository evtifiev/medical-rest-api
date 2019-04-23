"""update module_permission table

Revision ID: c7a48ec7497a
Revises: 1123e430968c
Create Date: 2019-02-13 14:26:30.297174

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c7a48ec7497a'
down_revision = '1123e430968c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('module_permission',
                  sa.Column('value', sa.String(50)))


def downgrade():
    op.drop_column('module_permission', 'value')

