import logging
from datetime import datetime

import attr

from rabbit.tlog.db import DB
from rabbit.tlog.event import Event
from rabbit.tlog.queries import EventQueries

from sqlalchemy.sql import text
from sqlalchemy.sql.elements import TextClause


logging.getLogger(__name__).addHandler(logging.NullHandler())


@attr.s(slots=True)
class EventPersist:

    db = attr.ib(
        type=DB,
        default=DB()
        # validator=attr.validators.instance_of(DB)
        # init=False
    )
    _stmt = attr.ib(
        type=TextClause,
        default=text(EventQueries.INSERT_EVENT.value),
        validator=attr.validators.instance_of(TextClause)
    )
    # _data = attr.ib(
    #     type=bytes,
    #     validator=attr.validators.instance_of(bytes),
    #     init=False
    # )

    def save(self, data: bytes) -> None:
        event = Event(body=data, created_at=datetime.utcnow())
        stmt = self._stmt.bindparams(
            body=event.body,
            status=event.status,
            created_at=event.created_at,
            created_by=event.created_by
        )
        logging.debug(f'Saving event: [{event}]')
        logging.info(f'Event saved.')
        self.db.execute(stmt)

    # def _configure(self, data: bytes) -> None:
    #     self._data = data
    #     self._db = self._get_db_connection()
    #     attr.validate(self)
    #     self._configure_db()

    # def _get_db_connection(self) -> DB:
    #     return DB()

    # def _configure_db(self) -> None:
    #     self._db.configure()
