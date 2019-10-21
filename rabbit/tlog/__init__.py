import json
import logging
from functools import wraps

from rabbit.tlog.queries import EventQueries
from rabbit.tlog.db import DB
from rabbit.tlog.event_persist import EventPersist


def persist_event(function):
    logging.debug(f'caller: {function}')

    @wraps(function)
    def save(*args, **kwargs):
        process_result = function(*args, **kwargs)
        e = EventPersist()
        e.save(process_result)
        logging.debug(f'Saving event: [{process_result}]')
        return process_result
    return save


@persist_event
def echo_persist_job(data: bytes) -> bytes:
    logging.info(
        'Using the persistent callable to process subscribe events.'
        ' This stream is compatible with the '
        'polling-publisher implementation'
    )

    data_response = json.loads(data)
    return bytes(
        json.dumps(data_response),
        'utf-8'
    )
