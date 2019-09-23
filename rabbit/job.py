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

        pargs = None
        if len(args) > 0:
            pargs = json.loads(args[0])
        else:
            pargs = json.dumps(args)

        return json.dumps(dict(
            positional_arguments=pargs,
            keyword_arguments=kwargs
        ))
