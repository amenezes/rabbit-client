"""create event table

Revision ID: eae5e199b5bc
Revises: 
Create Date: 2019-10-02 20:32:49.954323

"""
from datetime import datetime

from alembic import op

import sqlalchemy as sa
from sqlalchemy.schema import (
    CreateSchema,
    CreateSequence,
    DropSchema,
    DropSequence,
    Sequence
)


# revision identifiers, used by Alembic.
revision = 'eae5e199b5bc'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute(CreateSchema('tipos')),
    op.execute(CreateSequence(Sequence(name='id_seq', schema='tipos'))),
    op.create_table(
        'event',
        sa.Column(
            'id',
            sa.Integer,
            Sequence('id_seq'),
            primary_key=True
        ),
        sa.Column('body', sa.LargeBinary, nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime,
            default=datetime.utcnow
        ),
        sa.Column('created_by', sa.String(100)),
        sa.Column('status', sa.Boolean),
        schema='tipos'
    )


def downgrade():
    op.drop_table('event', schema='tipos')
    op.execute(DropSequence(Sequence(name='id_seq', schema='tipos')))
    op.execute(DropSchema('tipos'))
