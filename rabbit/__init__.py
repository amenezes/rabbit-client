import logging

from .__version__ import __version__

logger = logging.getLogger("rabbit-client")
logger.addHandler(logging.NullHandler())
