import logging
from datetime import datetime

import attr

from rabbit.tlog.core import singleton
from rabbit.tlog.db import DB
from rabbit.tlog.event import Event
from rabbit.tlog.queries import EventQueries

from sqlalchemy.sql import text


logging.getLogger(__name__).addHandler(logging.NullHandler())


@attr.s(slots=True)
class EventPersist:

    def save(self, data: bytes) -> None:
        self._is_valid(data)
        db = self._get_db_connection()
        stmt = text(EventQueries.INSERT_EVENT.value)
        event = Event(body=data, created=datetime.utcnow())
        stmt = stmt.bindparams(
            body=event.body,
            status=event.status,
            created=event.created
        )
        logging.debug(f'Saving event: [{event}]')
        db.execute(stmt)

    @singleton
    def _get_db_connection(self) -> DB:
        return DB()

    def _is_valid(self, data: bytes) -> None:
        if not isinstance(data, bytes):
            raise TypeError('data must be bytes.')
