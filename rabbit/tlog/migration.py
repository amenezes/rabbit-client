import configparser
import logging
import os
from pathlib import Path
from typing import Optional

import attr

logging.getLogger(__name__).addHandler(logging.NullHandler())


@attr.s
class Migration:
    driver = attr.ib(
        type=str,
        default=os.getenv(
            "DATABASE_DRIVER", "postgresql://postgres:postgres@localhost:5432/db"
        ),
        validator=attr.validators.instance_of(str),
    )
    _alembic_file = attr.ib(
        type=Optional[str],
        default=os.getenv("ALEMBIC_FILE"),
        validator=attr.validators.optional(validator=attr.validators.instance_of(str)),
    )
    _script_location = attr.ib(
        type=Optional[str],
        default=os.getenv("SCRIPT_LOCATION"),
        validator=attr.validators.optional(validator=attr.validators.instance_of(str)),
    )

    def __attrs_post_init__(self) -> None:
        logging.debug(str(self))
        self.configure()
        self.apply()

    @property
    def alembic_file(self) -> str:
        if not self._alembic_file:
            return Path(f"{Path(__file__).parent.parent}/alembic.ini").as_posix()
        return self._alembic_file

    @property
    def script_location(self) -> str:
        if not self._script_location:
            return Path(f"{Path(__file__).parent.parent}/migrations").as_posix()
        return self._script_location

    def configure(self) -> None:
        migrations_config = configparser.ConfigParser()
        migrations_config.read(self.alembic_file)
        migrations_config.set("alembic", "script_location", str(self.script_location))
        migrations_config.set("alembic", "sqlalchemy.url", str(self.driver))
        with open(self.alembic_file, "w+") as alembic_config:
            migrations_config.write(alembic_config)

    def apply(self) -> None:
        os.system(f"alembic -c {self.alembic_file} upgrade head")
