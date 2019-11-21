import asyncio
import json
import logging
import os
from typing import Optional

import attr

from rabbit.publish import Publish
from rabbit.tlog.db import DB
from rabbit.tlog.event import Event, events


logging.getLogger(__name__).addHandler(logging.NullHandler())


@attr.s(slots=True, frozen=True)
class PollingPublisher:

    db = attr.ib(
        type=DB,
        validator=attr.validators.instance_of(DB)
    )
    publish = attr.ib(
        type=Publish,
        validator=attr.validators.instance_of(Publish)
    )

    async def run(self):
        logging.info("Starting polling-publisher")
        self.db.configure()
        while True:
            await asyncio.sleep(
                float(os.getenv('POLLING_STANDBY_TIME', 60))
            )
            event = await self._retrieve_event()
            if not event:
                logging.debug('There are no new events to be processed...')
            else:
                logging.info(
                    f'Event id:{event.id} sent to message broker.'
                )
                await self._send_and_update(event)

    async def _send_and_update(self, event: Event) -> None:
        try:
            payload = self._format_payload(event)
            logging.debug(f"Payload: {payload}")

            await self.publish.send_event(payload)
            await self._update_event_status(event)
            logging.info(
                'Event successfully sent and updated!'
                f' [event_id: {event.id}]'
            )
        except Exception as err:
            logging.error(
                f"Failed to publish event id: {event.id}"
            )
            logging.error(err)
            await asyncio.sleep(10)

    def _format_payload(self, event) -> bytes:
        payload = json.loads(event.body)
        payload.update({'createdBy': event.created_by})
        return bytes(json.dumps(payload), 'utf-8')

    async def _retrieve_event(self) -> Optional[Event]:
        event = await self.db.get_oldest_event()
        logging.debug(f"Oldest event retrieved: {event}")

        if not event:
            return None

        logging.debug(f"Successfully recovered event.")
        return Event(
            id=event.id,
            body=event.body,
            created_at=event.created_at,
            created_by=event.created_by,
            status=event.status
        )

    async def _update_event_status(self, event: Event) -> None:
        stmt = events.update().where(events.c.id == event.id).values(
            status=True
        )
        await self.db.exec(stmt)
