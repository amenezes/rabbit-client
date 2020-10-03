from contextlib import suppress

import attr

from rabbit import logger
from rabbit.utils import loop


@attr.s(slots=True, frozen=True)
class Observer:

    _observers = attr.ib(
        type=list, factory=list, validator=attr.validators.instance_of(list)
    )

    def attach(self, observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer) -> None:
        with suppress(ValueError):
            self._observers.remove(observer)

    def notify(self, modifier=None) -> None:
        for observer in self._observers:
            if modifier != observer:
                logger.debug(f"{observer.__class__} notified")
                loop().create_task(observer.configure())

    def __len__(self) -> int:
        return len(self._observers)

    def __contains__(self, value):
        if value in (self._observers):
            return True
        return False

    @property
    def observers(self):
        return self._observers
