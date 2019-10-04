import os
from typing import Any

import attr

from sqlalchemy import create_engine
from sqlalchemy.sql.elements import TextClause


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

    def __attrs_post_init__(self) -> None:
        self._engine = create_engine(self.driver)
        self._connection = self._engine.connect()

    def execute(self, stmt, **kwargs) -> Any:
        if not isinstance(stmt, TextClause):
            raise TypeError(
                'stmt is not instance of sqlalchemy.sql.elements.TextClause'
            )
        return self._connection.execute(stmt, kwargs)
