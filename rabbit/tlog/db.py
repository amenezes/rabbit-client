import logging
import os
import time
from datetime import datetime

import attr
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

from rabbit import OperationError
from rabbit.tlog import Event, Migration, events

logging.getLogger(__name__).addHandler(logging.NullHandler())


@attr.s(slots=True)
class DB:
    driver = attr.ib(
        type=str,
        default=os.getenv(
            "DATABASE_DRIVER", "postgresql://postgres:postgres@localhost:5432/db"
        ),
        validator=attr.validators.instance_of(str),
    )
    _migration = attr.ib(
        type=Migration,
        factory=Migration,
        validator=attr.validators.instance_of(Migration),
    )
    _engine = attr.ib(default=None)
    _connection = attr.ib(default=None)
    _session = attr.ib(default=None)

    def __attrs_post_init__(self):
        self.configure()

    @property
    def connection(self):
        return self._connection

    @connection.setter
    def connection(self, value):
        if self._connection:
            self._connection.invalidate()
        self._connection = value

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        if self._session:
            self._session.invalidate()
        self._session = value

    @property
    def alembic_file(self):
        return self._migration.alembic_file

    @property
    def script_location(self):
        return self._migration.script_location

    def configure(self) -> None:
        self._engine = create_engine(self.driver, pool_pre_ping=True)
        Session = sessionmaker(bind=self._engine)
        self._session = Session()

        self._connection = self._engine.connect()
        try:
            self._connection = self._engine.connect()
        except Exception:
            self._reconnect()

    def _reconnect(self):
        logging.error("Failed to connect to database. Trying again in 10 seconds")
        logging.debug(f"DB({attr.asdict(self)})")
        time.sleep(10)
        self.configure()

    async def exec(self, command, params={}):
        try:
            self._connection.execute(command, [params])
        except OperationalError:
            self._reconnect()
            await self.exec(command, params)

    async def save(self, data: bytes, user: str = "anonymous") -> None:
        e = Event(body=data, created_at=datetime.utcnow(), created_by=user)
        ins = events.insert().values(
            body=e.body,
            status=e.status,
            created_at=e.created_at,
            created_by=e.created_by,
        )
        ins.compile().params

        try:
            logging.debug(f"Saving event: [{e}]")
            await self.exec(ins)
            logging.info(f"Event saved.")
        except OperationalError:
            self._session.rollback()
            self._reconnect()
            raise OperationError("Failed to store event.")

    async def get_oldest_event(self):
        try:
            event = (
                self._session.query(events)
                .filter_by(status=False)
                .order_by("created_at")
                .first()
            )
            if not event:
                return None
            return Event(
                event.body, event.id, event.created_at, event.created_by, event.status,
            )
        except OperationalError:
            self._reconnect()
