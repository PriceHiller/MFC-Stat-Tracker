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

import asyncio

from dataclasses import dataclass
from typing import Any


@dataclass
class Event:
    name: str
    content: Any


class EventListener:

    def __init__(self):
        """This allows this class to be inheritable to extend events to other classes"""
        cls = self.__class__
        try:
            getattr(cls, "_listening_events")
        except AttributeError:
            setattr(cls, "_listening_events", {})

    def listen(self, event: str):
        event = str(event)
        _listening_events: dict = self.__getattribute__("_listening_events")

        def decorator(function):
            if not _listening_events.get(event):
                _listening_events[event] = []
            _listening_events[event].append(function)

        return decorator

    async def parse_event(self, event: Event):
        _listening_events: dict = self.__getattribute__("_listening_events")
        if events := _listening_events.get(event.name, None):
            tasks = []
            for listener in events:
                tasks.append(listener(event))
            await asyncio.gather(*tasks)


listen = EventListener().listen
parse = EventListener().parse_event
