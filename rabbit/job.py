import json
import logging

import attr


logging.getLogger(__name__).addHandler(logging.NullHandler())


@attr.s(slots=True, frozen=True)
class SampleJob:

    @staticmethod
    def echo_job(*args, **kwargs) -> str:
        logging.info(
            'Using the standard callable to process subscribe events.'
        )

        return json.dumps(dict(
            positional_arguments=json.dumps(args),
            keyword_arguments=kwargs
        ))

    async def async_echo_job(self, *args, **kwargs):
        return self.echo_job(*args, **kwargs)
