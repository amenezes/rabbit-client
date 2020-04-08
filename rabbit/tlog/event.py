import os
from datetime import datetime
from typing import Optional

import attr
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    LargeBinary,
    MetaData,
    String,
    Table,
)
from sqlalchemy.orm import mapper
from sqlalchemy.schema import Sequence

metadata = MetaData(schema=str(os.getenv("EVENT_SCHEMA", "my_schema")))
events = Table(
    "event",
    metadata,
    Column("body", LargeBinary, nullable=False),
    Column(
        "id",
        Integer,
        Sequence(name="id_seq", schema=str(os.getenv("EVENT_SCHEMA", "my_schema"))),
        primary_key=True,
    ),
    Column("created_at", DateTime),
    Column("created_by", String(100)),
    Column("status", Boolean),
    schema=str(os.getenv("EVENT_SCHEMA", "my_schema")),
)


@attr.s
class Event:

    body = attr.ib(type=bytes, validator=attr.validators.instance_of(bytes))
    id = attr.ib(
        type=Optional[int],
        default=None,
        validator=attr.validators.optional(validator=attr.validators.instance_of(int)),
    )
    created_at = attr.ib(
        type=Optional[datetime],
        default=None,
        validator=attr.validators.optional(
            validator=attr.validators.instance_of(datetime)
        ),
    )
    created_by = attr.ib(
        type=str, default="", validator=attr.validators.instance_of(str)
    )
    status = attr.ib(
        type=bool, default=False, validator=attr.validators.instance_of(bool)
    )


mapper(Event, events)
