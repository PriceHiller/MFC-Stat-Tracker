import logging

from dataclasses import dataclass

log = logging.getLogger(__name__)


class EventListener:
    listening_events: dict[str, list[callable]] = {}
    loaded_events: dict[str, list[hash]] = {}

    @classmethod
    def listen(cls, event: str):
        def decorator(function):
            if not cls.listening_events.get(event, None):
                cls.listening_events[event] = []
                cls.loaded_events[event] = []
            if function.__code__ not in cls.loaded_events[event]:
                cls.listening_events[event].append(function)
                cls.loaded_events[event].append(function.__code__)

        return decorator

    @classmethod
    def parse(cls, event_name: str, event_content: str):
        if listening_events := cls.listening_events.get(event_name):
            for event in listening_events:
                try:
                    event(event_content)
                except TypeError:
                    log.error(f"Event unable to accept event content: {event_content}")


@dataclass
class Event:
    login: str = "Login"
    punishment: str = "Punishment"
    match_state: str = "MatchState"
    score_feed: str = "Scorefeed"
    kill_feed: str = "Killfeed"
