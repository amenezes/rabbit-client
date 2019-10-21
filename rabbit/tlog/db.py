import logging
import os
import time
from typing import Any

import attr

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql.elements import TextClause


logging.getLogger(__name__).addHandler(logging.NullHandler())


@attr.s(slots=True)
class DB:
    driver = attr.ib(
        type=str,
        default=os.getenv(
            'DATABASE_DRIVER',
            'postgresql://postgres:postgres@localhost:5432/db'
        )
    )
    _engine = attr.ib(default=None)
    _connection = attr.ib(default=None)
    _stmt = attr.ib(
        init=False,
        type=TextClause,
        validator=attr.validators.instance_of(TextClause)
    )

    def configure(self) -> None:
        self._engine = create_engine(self.driver)
        try:
            self._connection = self._engine.connect()
        except Exception:
            logging.error('Failed to connect to database. Trying again in 10 seconds')
            time.sleep(10)
            self.configure()

    def execute(self, stmt: TextClause, **kwargs) -> Any:
        self._configure_stmt(stmt)
        result = None
        try:
            result = self._connection.execute(stmt, kwargs)
        except OperationalError:
            self.configure()
            self.execute(stmt)
        return result

    def _configure_stmt(self, stmt: TextClause) -> None:
        self._stmt = stmt
        attr.validate(self)
