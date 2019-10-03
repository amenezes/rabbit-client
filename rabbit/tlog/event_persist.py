import json
import logging

from rabbit.tlog.core import singleton
from rabbit.tlog.db import DB
from rabbit.tlog.event import Event
from rabbit.tlog.queries import EventQueries

from sqlalchemy.sql import text

logging.getLogger(__name__).addHandler(logging.NullHandler())


class EventPersist:

    @singleton
    def _get_db_connection(self):
        return DB()

    def save(self, data):
        db = self._get_db_connection()
        stmt = text(EventQueries.INSERT_EVENT.value)
        event = Event(body=bytes(json.dumps(data), 'utf-8'))
        stmt = stmt.bindparams(
            body=event.body,
            status=event.status,
            created=event.created
        )
        logging.debug(f'Saving event: [{event}]')
        db.execute(stmt)
