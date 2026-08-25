"""Add patient name to predictions.

Revision ID: 8f2c1a6d4b90
Revises: c39ef82fba48
Create Date: 2026-08-24 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '8f2c1a6d4b90'
down_revision = 'c39ef82fba48'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('prediction', sa.Column('patient_name', sa.String(length=100), nullable=True))


def downgrade():
    op.drop_column('prediction', 'patient_name')
