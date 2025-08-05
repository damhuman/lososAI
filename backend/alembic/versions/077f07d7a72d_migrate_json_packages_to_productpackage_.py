"""Migrate JSON packages to ProductPackage table

Revision ID: 077f07d7a72d
Revises: bd93ea366fcd
Create Date: 2025-08-05 12:34:47.215649

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '077f07d7a72d'
down_revision = 'bd93ea366fcd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass