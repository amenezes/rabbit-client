import configparser
import os
from pathlib import Path

import attr

from rabbit import logger


@attr.s
class Migration:
    driver = attr.ib(
        type=str,
        default=os.getenv(
            "DATABASE_DRIVER", "postgresql://postgres:postgres@localhost:5432/db"
        ),
        validator=attr.validators.instance_of(str),
    )
    alembic_file = attr.ib(
        type=str,
        default=os.getenv(
            "ALEMBIC_FILE",
            Path(f"{Path(__file__).parent.parent}/alembic.ini").as_posix(),
        ),
        validator=attr.validators.instance_of(str),
    )
    script_location = attr.ib(
        type=str,
        default=os.getenv(
            "SCRIPT_LOCATION",
            Path(f"{Path(__file__).parent.parent}/migrations").as_posix(),
        ),
        validator=attr.validators.instance_of(str),
    )

    def __attrs_post_init__(self) -> None:
        logger.debug(str(self))
        self.configure()
        self.apply()

    def configure(self) -> None:
        migrations_config = configparser.ConfigParser()
        migrations_config.read(self.alembic_file)
        migrations_config.set("alembic", "script_location", self.script_location)
        migrations_config.set("alembic", "sqlalchemy.url", self.driver)
        with open(self.alembic_file, "w+") as alembic_config:
            migrations_config.write(alembic_config)

    def apply(self) -> None:
        os.system(f"alembic -c {self.alembic_file} upgrade head")
