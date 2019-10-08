import logging
import os
from typing import Any
import time

import attr


logging.getLogger(__name__).addHandler(logging.NullHandler())


try:
    from sqlalchemy import create_engine
    from sqlalchemy.sql.elements import TextClause
    from sqlalchemy.exc import OperationalError
except ModuleNotFoundError:
    logging.error('To use the Polling-Publisher feature Install SQLAlchemy')


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

    def configure(self) -> None:
        self._engine = create_engine(self.driver)
        try:
            self._connection = self._engine.connect()
        except Exception:
            logging.error(f'Failed to connect to database: {self.driver}')
            time.sleep(10)
            self.configure()

    def execute(self, stmt, **kwargs) -> Any:
        if not isinstance(stmt, TextClause):
            raise TypeError(
                'stmt is not instance of sqlalchemy.sql.elements.TextClause'
            )
        result = None
        logging.debug(stmt)
        try:
            result = self._connection.execute(stmt, kwargs)
        except OperationalError:
            self.configure()
            logging.debug(stmt)
            self.execute(stmt)

        return result
