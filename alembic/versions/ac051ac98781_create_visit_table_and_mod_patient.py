"""create visitor table and mod patient

Revision ID: ac051ac98781
Revises: 6983a4d7b67f
Create Date: 2019-04-18 08:39:03.842706

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ac051ac98781'
down_revision = '6983a4d7b67f'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('patient', 'source_of_financing')
    op.add_column('patient',
                  sa.Column('middle_name', sa.String(70)))

    # Таблица визиты пациентов
    op.create_table(
        'visit',
        sa.Column('id', sa.Integer, unique=True, nullable=False, primary_key=True),
        sa.Column('created', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column('modified', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column('creator_id', sa.Integer, sa.ForeignKey('user.id'), nullable=True),
        sa.Column('editor_id', sa.Integer, sa.ForeignKey('user.id'), nullable=True),
        sa.Column('schedule_id', sa.Integer, sa.ForeignKey('schedule.id'), nullable=True),
        sa.Column('patient_id', sa.Integer, sa.ForeignKey('patient.id'), nullable=True),
        sa.Column('doctor_id', sa.Integer, sa.ForeignKey('doctor.id'), nullable=True),
        sa.Column('source_of_financing', sa.Integer, nullable=True)
    )


def downgrade():
    pass
