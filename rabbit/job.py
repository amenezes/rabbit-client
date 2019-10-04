import json
import logging

import attr

from rabbit import persist_event


logging.getLogger(__name__).addHandler(logging.NullHandler())


@attr.s(slots=True, frozen=True)
class SampleJob:

    @staticmethod
    def echo_job(data: bytes) -> bytes:
        logging.info(
            'Using the standard callable to process subscribe events.'
        )

        data_response = json.loads(data)
        return bytes(
            json.dumps(data_response),
            'utf-8'
        )

    async def async_echo_job(self, data: bytes) -> bytes:
        return self.echo_job(data)

    @staticmethod
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
