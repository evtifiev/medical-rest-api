"""create schedule

Revision ID: 6983a4d7b67f
Revises: fbc06e292b02
Create Date: 2019-04-03 22:18:26.959672

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6983a4d7b67f'
down_revision = 'fbc06e292b02'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('schedule',
                  sa.Column('is_busy', sa.Boolean, default=False))


def downgrade():
    op.drop_column('schedule', 'is_busy')
