"""
Example Proof of Concept
========================

>>> @EventListener.listen(EventType.match_state)
>>> async def another_state(event: Event):
>>>     log.info(event.content)

Example EventType
=================
>>> class EventType(enum.Enum):
>>>     LOGIN: str = "Login"
>>>     PUNISHMENT: str = "Punishment"
>>>     MATCH_STATE: str = "MatchState"
>>>     SCORE_FEED: str = "Scorefeed"
>>>     KILL_FEED: str = "Killfeed"
>>>
>>>     def __str__(self):
>>>         return self.value

"""

import logging
import asyncio

from dataclasses import dataclass
from typing import Any

log = logging.getLogger(__name__)


@dataclass
class Event:
    name: str
    content: Any


class EventListener:
    _listening_events: dict[str, list[callable]] = {}

    @classmethod
    def listen(cls, event: str):
        event = str(event)

        def decorator(function):
            if not cls._listening_events.get(event):
                cls._listening_events[event] = []
            cls._listening_events[event].append(function)

        return decorator

    @classmethod
    async def parse_event(cls, event: Event):
        log.debug(f"Parsing event: \"{event.name}\": \"{event.content}\"")
        if events := cls._listening_events.get(event.name, None):
            tasks = []
            for listener in events:
                log.debug(f"Listener \"{listener.__module__}.{listener.__name__}\" handling "
                          f"\"{event.name}: {event.content}\"")
                tasks.append(listener(event))
            await asyncio.gather(*tasks)
