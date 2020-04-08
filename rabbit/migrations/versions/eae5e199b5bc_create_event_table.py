"""create event table

Revision ID: eae5e199b5bc
Revises: 
Create Date: 2019-10-02 20:32:49.954323

"""
import os
from datetime import datetime

import sqlalchemy as sa
from alembic import context, op
from sqlalchemy.schema import (CreateSchema, CreateSequence, DropSchema,
                               DropSequence, Sequence)

# revision identifiers, used by Alembic.
revision = "eae5e199b5bc"
down_revision = None
branch_labels = None
depends_on = None

config = context.config
url = config.get_main_option("sqlalchemy.url")


def upgrade():
    if url.lower().startswith("postgres"):
        op.execute(CreateSchema(str(os.getenv("EVENT_SCHEMA", "my_schema"))))
    op.execute(
        CreateSequence(
            Sequence(name="id_seq", schema=str(os.getenv("EVENT_SCHEMA", "my_schema")))
        )
    ),
    op.create_table(
        "event",
        sa.Column("id", sa.Integer, Sequence("id_seq"), primary_key=True),
        sa.Column("body", sa.LargeBinary, nullable=False),
        sa.Column("created_at", sa.DateTime, default=datetime.utcnow),
        sa.Column("created_by", sa.String(100)),
        sa.Column("status", sa.Boolean),
        schema=str(os.getenv("EVENT_SCHEMA", "my_schema")),
    )


def downgrade():
    op.drop_table("event", schema=str(os.getenv("EVENT_SCHEMA", "my_schema")))
    op.execute(
        DropSequence(
            Sequence(name="id_seq", schema=str(os.getenv("EVENT_SCHEMA", "my_schema")))
        )
    )
    if url.lower().startswith("postgres"):
        op.execute(DropSchema(str(os.getenv("EVENT_SCHEMA", "my_schema"))))
