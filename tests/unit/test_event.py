import json
from datetime import datetime

import attr
import pytest

from rabbit.tlog import Event

CREATED_AT = datetime.utcnow()
PAYLOAD = {
    "paginas": ["abcd", "123"],
    "documento": 123,
    "descricao": "abc",
}


@pytest.fixture
def event():
    return Event(body=bytes(json.dumps(PAYLOAD), "utf-8"), created_at=CREATED_AT)


def test_attributes(event):
    values = [bytes(json.dumps(PAYLOAD), "utf-8"), CREATED_AT]
    for value in values:
        assert value in attr.asdict(event).values()
