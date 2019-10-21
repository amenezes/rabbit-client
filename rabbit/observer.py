import logging

import attr


logging.getLogger(__name__).addHandler(logging.NullHandler())


@attr.s(slots=True, frozen=True)
class Observer:

    _observers = attr.ib(
        type=list,
        default=[],
        validator=attr.validators.instance_of(list)
    )

    def attach(self, observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer) -> None:
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    def notify(self, loop, modifier=None) -> None:
        for observer in self._observers:
            if modifier != observer:
                logging.debug(f'{observer.__class__} notified')
                loop.create_task(observer.configure())
