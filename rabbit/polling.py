import asyncio
import json
import logging
import os

import attr

from rabbit.publish import Publish
from rabbit.tlog.db import DB
from rabbit.tlog.event import Event, events

logging.getLogger(__name__).addHandler(logging.NullHandler())


@attr.s(slots=True, frozen=True)
class PollingPublisher:

    publish = attr.ib(type=Publish, validator=attr.validators.instance_of(Publish))
    db = attr.ib(type=DB, factory=DB, validator=attr.validators.instance_of(DB))

    async def run(self):
        logging.info("Starting polling-publisher")
        self.db.configure()
        while True:
            await asyncio.sleep(float(os.getenv("POLLING_STANDBY_TIME", 10)))
            await self._retrieve_event()

    async def _retrieve_event(self) -> None:
        event = await self.db.get_oldest_event()
        logging.debug(f"event retrieved: {event}")
        if not event:
            return None
        logging.debug(f"Successfully recovered event.")
        await self.send_event(event)

    async def send_event(self, event):
        try:
            payload = self._format_payload(event)
            await self.publish.send_event(payload)
            await self._update_event_status(event)
            logging.info(f"Event(id={event.id}) successfully sent and updated!")
        except Exception as err:
            logging.error(f"Failed to publish Event(id={event.id})")
            logging.error(err)
            await asyncio.sleep(10)

    def _format_payload(self, event) -> bytes:
        payload = json.loads(event.body)
        payload.update({"createdBy": event.created_by})
        return bytes(json.dumps(payload), "utf-8")

    async def _update_event_status(self, event: Event) -> None:
        stmt = events.update().where(events.c.id == event.id).values(status=True)
        await self.db.exec(stmt)
