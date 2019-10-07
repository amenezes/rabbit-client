"""create event table

Revision ID: eae5e199b5bc
Revises: 
Create Date: 2019-10-02 20:32:49.954323

"""
from datetime import datetime
from alembic import op

import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eae5e199b5bc'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'event',
        sa.Column('id', sa.Integer, primary_key=True, unique=True, autoincrement=True),
        sa.Column('body', sa.Binary, nullable=False),
        sa.Column('created', sa.DateTime, default=datetime.utcnow),
        sa.Column('status', sa.Boolean)
    )


def downgrade():
    op.drop_table('event')
