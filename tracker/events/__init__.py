import logging
import asyncio

from dataclasses import dataclass

log = logging.getLogger(__name__)


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
    async def parse_event(cls, event_name: str, event_content: str):
        log.info(f"Parsing event: \"{event_name}\": \"{event_content.strip()}\"")
        if events := cls._listening_events.get(event_name):
            tasks = []
            for event in events:
                log.info(f"Listener \"{event.__module__}.{event.__name__}\" handling "
                         f"\"{event_name}: {event_content.strip()}\"")
                tasks.append(event(event_content))
            await asyncio.gather(*tasks)


@dataclass
class Event:
    login: str = "Login"
    punishment: str = "Punishment"
    match_state: str = "MatchState"
    score_feed: str = "Scorefeed"
    kill_feed: str = "Killfeed"


@EventListener.listen(Event.match_state)
async def another_state(event_content: str):
    log.info(event_content)

