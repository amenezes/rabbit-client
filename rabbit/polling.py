import asyncio
import logging

import attr

from rabbit.client import AioRabbitClient
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

    async def configure(self):
        await self.publish.configure()

    async def run(self) -> None:
        event = await self._retrieve_event()
        try:
            await self.publish.send_event(event.body)
            await self._update_event_status(event)
        except Exception:
            asyncio.sleep(10)
            logging.error(
                f"Failed to publish event: [id: {event.identity}]"
            )

    async def _retrieve_event(self) -> Event:
        stmt = text(EventQueries.OLDEST_EVENT.value)
        result = self.db.execute(stmt).first()
        logging.debug(f"Event retrieved: [{result.values()}]")
        event = Event(
            body=bytes(result[1]),
            status=result[2]
        )
        event.identity = result[0]
        return event

    async def _update_event_status(self, event: Event) -> None:
        stmt = text(EventQueries.UPDATE_EVENT_STATUS.value)
        stmt = stmt.bindparams(identity=event.identity)
        self.db.execute(stmt)
