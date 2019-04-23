"""create doctor, doctor_specialization table

Revision ID: 03f6f8d70c43
Revises: c7a48ec7497a
Create Date: 2019-03-31 23:47:22.551873

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '03f6f8d70c43'
down_revision = 'c7a48ec7497a'
branch_labels = None
depends_on = None


def upgrade():
    # Таблица специализация врачей
    op.create_table(
        'doctor_specialization',
        sa.Column('id', sa.Integer, unique=True, nullable=False, primary_key=True),
        sa.Column('created', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column('modified', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column('name', sa.String(120), nullable=False, unique=True)
    ),
    # Таблица список врачей ведущих прием
    op.create_table(
        'doctor',
        sa.Column('id', sa.Integer, unique=True, nullable=False, primary_key=True),
        sa.Column('created', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column('modified', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column('user_id',  sa.Integer, sa.ForeignKey('user.id'), nullable=True),
        sa.Column('doctor_specialization_id',  sa.Integer, sa.ForeignKey('doctor_specialization.id'), nullable=True),
        sa.Column('creator_id', sa.Integer, sa.ForeignKey('user.id'), nullable=True),
    )


def downgrade():
    op.drop_table('position')
    op.drop_table('department')
