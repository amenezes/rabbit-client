import asyncio
import logging
import os
from typing import Any, Optional

import attr

from rabbit.publish import Publish
from rabbit.tlog.db import DB
from rabbit.tlog.event import Event
from rabbit.tlog.queries import EventQueries

from sqlalchemy.sql import text


logging.getLogger(__name__).addHandler(logging.NullHandler())


@attr.s(slots=True, frozen=True)
class PollingPublisher:

    publish = attr.ib(
        type=Publish,
        validator=attr.validators.instance_of(Publish)
    )
    db = attr.ib(
        type=DB,
        default=DB(),
        validator=attr.validators.instance_of(DB)
    )

    async def run(self):
        self.db.configure()
        logging.info("Starting polling-publisher")
        while True:
            await asyncio.sleep(os.getenv('POLLING_STANDBY_TIME', 60))
            event = await self._retrieve_event()
            if not event:
                logging.debug('There are no new events to be processed...')
            else:
                logging.debug(
                    f'Event id:{event.identity} successfully processed.'
                )
                await self._send_and_update(event)

    async def _send_and_update(self, event: Event) -> None:
        try:
            await self.publish.send_event(event.body)
            await self._update_event_status(event)
            logging.debug(
                'Event successfully sent and updated!'
                f' [event_id: {event.identity}]'
            )
        except Exception:
            await asyncio.sleep(10)
            logging.error(
                f"Failed to publish event id: {event.identity}"
            )

    async def _retrieve_event(self) -> Optional[Event]:
        result = await self._get_result()
        if result:
            event = await self._assemble_event(result)
            return event
        return None

    async def _get_result(self) -> Optional[Any]:
        stmt = text(EventQueries.OLDEST_EVENT.value)
        result = self.db.execute(stmt)
        if result:
            logging.debug(f"Successfully recovered event.")
            return result.first()
        return None

    async def _assemble_event(self, data: tuple) -> Event:
        identity, body, status = data
        event = Event(
            identity=identity,
            body=bytes(body),
            status=status
        )
        return event

    async def _update_event_status(self, event: Event) -> None:
        stmt = text(EventQueries.UPDATE_EVENT_STATUS.value)
        stmt = stmt.bindparams(identity=event.identity)
        self.db.execute(stmt)
