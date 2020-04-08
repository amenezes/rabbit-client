from pathlib import Path

import pytest

from rabbit.tlog import Migration


@pytest.fixture
def current_dir():
    return Path(__file__).parent.as_posix()


@pytest.fixture
def basepath(current_dir):
    base = Path(current_dir).parent.parent.as_posix()
    return f"{base}/rabbit"


def test_alembic_file(basepath):
    migration = Migration()
    assert migration.alembic_file == f"{basepath}/alembic.ini"


def test_alembic_file_custom(current_dir):
    migration = Migration(alembic_file=f"{current_dir}/alembic.ini")
    assert migration.alembic_file == f"{current_dir}/alembic.ini"


def test_script_location(current_dir, basepath):
    migration = Migration(alembic_file=f"{current_dir}/alembic.ini")
    assert migration.script_location == f"{basepath}/migrations"


def test_script_location_custom(current_dir, basepath):
    migration = Migration(
        alembic_file=f"{current_dir}/alembic.ini",
        script_location=f"{current_dir}/migrations",
    )
    assert migration.script_location == f"{current_dir}/migrations"
