import asyncio
import logging
from typing import Optional

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

    async def configure(self) -> None:
        if not self.publish.client:
            await self.publish.configure()
            await asyncio.sleep(5)

    async def run(self) -> None:
        event = await self._retrieve_event()
        if not event:
            logging.debug('There are no new events...')
        else:
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
            asyncio.sleep(10)
            logging.error(
                f"Failed to publish event id: {event.identity}"
            )

    async def _retrieve_event(self) -> Optional[Event]:
        stmt = text(EventQueries.OLDEST_EVENT.value)
        result = self.db.execute(stmt).first()
        event = None
        if result:
            logging.debug(f"Successfully recovered event: {result}")
            event = await self._assemble_event(result)
        return event

    async def _assemble_event(self, data) -> Event:
        event = Event(
            body=bytes(data[1]),
            status=data[2]
        )
        event.identity = data[0]
        return event

    async def _update_event_status(self, event: Event) -> None:
        stmt = text(EventQueries.UPDATE_EVENT_STATUS.value)
        stmt = stmt.bindparams(identity=event.identity)
        self.db.execute(stmt)
