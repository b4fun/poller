import abc
import dataclasses
from turtle import back
import typing

from .entity import Entity
from .entity import EntityStorage


FetchEntitiesFunc = typing.Callable[[], typing.Iterable[Entity]]
CheckSaveEntityFunc = typing.Callable[[Entity], bool]
LogFunc = typing.Callable[[str], None]
ConsumeEntityFunc = typing.Callable[[Entity], None]


@dataclasses.dataclass
class PollerProvider:
    
    storage: EntityStorage
    fetch_entities: FetchEntitiesFunc
    should_save_entity: CheckSaveEntityFunc
    log: LogFunc


class Poller:
    """Poller is responsible for polling entities and saving them."""

    def __init__(self, provider: PollerProvider):
        self.provider = provider

    def poll_once(self) -> typing.Iterable[Entity]:
        """Poll entities from remote."""
        for entity in self.provider.fetch_entities():
            if not self.provider.should_save_entity(entity):
                self.provider.log(f'should_save_entity returned False for {entity.id}')
                continue
            
            if self.provider.storage.has_entity(entity):
                self.provider.log(f'entity {entity.id} exists')
                continue

            yield entity

            self.provider.log(f'saving entity {entity.id}')
            self.provider.storage.save_entity(entity)


class Clock(metaclass=abc.ABCMeta):
    """Clock defines the mockable clock interface."""

    @abc.abstractmethod
    def time(self) -> float:
        """Get the current timestamp in seconds."""

    @abc.abstractmethod
    def sleep(self, seconds: float) -> None:
        """Sleep for the given number of seconds."""


def poll_until_exit(
    log: LogFunc,
    poll_interval_in_seconds: float,
    get_poll_provider: typing.Callable[[], PollerProvider],
    consume_entity: ConsumeEntityFunc,
    clock: typing.Optional[Clock] = None,
):
    """Poll entities until the process is terminated or failed."""
    if clock is None:
        import time
        clock = time

    while True:
        log('start polling attempt')
        started_at = clock.time()

        poller = Poller(get_poll_provider())

        for entity in poller.poll_once():
            consume_entity(entity)

        duration = clock.time() - started_at
        backoff = poll_interval_in_seconds - duration
        if backoff < 0:
            backoff = poll_interval_in_seconds
        log(f'polling attempt finished, sleep {backoff}s')
        time.sleep(backoff)