"""create schedule table

Revision ID: fbc06e292b02
Revises: 1df7295dde5d
Create Date: 2019-04-03 18:47:19.216939

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fbc06e292b02'
down_revision = '1df7295dde5d'
branch_labels = None
depends_on = None


def upgrade():
    # Таблица расписание врачей
    op.create_table(
        'schedule',
        sa.Column('id', sa.Integer, unique=True, nullable=False, primary_key=True),
        sa.Column('created', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column('modified', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column('date_start', sa.TIMESTAMP, nullable=False),
        sa.Column('date_end', sa.TIMESTAMP, nullable=False,),
        sa.Column('doctor_id', sa.Integer, sa.ForeignKey('doctor.id'), nullable=True),
        sa.Column('creator_id', sa.Integer, sa.ForeignKey('user.id'), nullable=True),
    )


def downgrade():
    op.drop_table('schedule')