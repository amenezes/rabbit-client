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
