import logging
import asyncio
import enum

from dataclasses import dataclass
from typing import Any

log = logging.getLogger(__name__)


class EventType(enum.Enum):
    login: str = "Login"
    punishment: str = "Punishment"
    match_state: str = "MatchState"
    score_feed: str = "Scorefeed"
    kill_feed: str = "Killfeed"


@dataclass
class Event:
    name: str
    content: Any


class EventListener:
    _listening_events: dict[str, list[callable]] = {}
    _loaded_events: dict[str, list] = {}

    @classmethod
    def listen(cls, event: str):
        def decorator(function):
            if not cls._listening_events.get(event, None):
                cls._listening_events[event] = []
                cls._loaded_events[event] = []
            if function.__code__ not in cls._loaded_events[event]:
                cls._listening_events[event].append(function)
                cls._loaded_events[event].append(function.__code__)

        return decorator

    @classmethod
    async def parse_event(cls, event: Event):
        log.info(f"Parsing event: \"{event.name}\": \"{event.content}\"")
        if events := cls._listening_events.get(event.name):
            tasks = []
            for listener in events:
                log.info(f"Listener \"{listener.__module__}.{listener.__name__}\" handling "
                         f"\"{event.name}: {event.content}\"")
                tasks.append(listener(event))
            await asyncio.gather(*tasks)


@EventListener.listen(EventType.match_state)
async def another_state(event: Event):
    log.info(event.content)
