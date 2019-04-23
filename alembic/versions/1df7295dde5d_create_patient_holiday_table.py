"""create patient, holiday table

Revision ID: 1df7295dde5d
Revises: 03f6f8d70c43
Create Date: 2019-04-03 03:38:03.217643

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1df7295dde5d'
down_revision = '03f6f8d70c43'
branch_labels = None
depends_on = None


def upgrade():
    # Таблица пациенты
    op.create_table(
        'patient',
        sa.Column('id', sa.Integer, unique=True, nullable=False, primary_key=True),
        sa.Column('created', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column('modified', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column('last_name', sa.String(90), nullable=True),
        sa.Column('first_name', sa.String(40), nullable=True),
        sa.Column('mobile', sa.String(80), nullable=True),
        sa.Column('source_of_financing', sa.Integer, nullable=True),
    )
    # Таблица праздничные дни
    op.create_table(
        'holiday',
        sa.Column('id', sa.Integer, unique=True, nullable=False, primary_key=True),
        sa.Column('created', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column('modified', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column('date', sa.TIMESTAMP, nullable=True),
        sa.Column('name', sa.String(90), nullable=True)
    )


def downgrade():
    op.drop_table('patient')
    op.drop_table('holiday')
