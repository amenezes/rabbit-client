import logging
from typing import Any, Dict

import attr


logging.getLogger(__name__).addHandler(logging.NullHandler())


@attr.s(slots=True, frozen=True)
class SampleJob:

    @staticmethod
    def echo_job(*args, **kwargs) -> Dict[str, Any]:
        logging.info(
            'Using the standard callable to process subscribe events.'
        )
        return dict(
            positional_arguments=args,
            keyword_arguments=kwargs
        )
