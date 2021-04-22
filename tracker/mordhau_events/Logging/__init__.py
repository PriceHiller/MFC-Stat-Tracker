import logging

from tracker.events import EventListener
from tracker.events import Event
from tracker.mordhau_events.type import EventType


log = logging.getLogger(__name__)


class LogEvents:

    @staticmethod
    @EventListener.listen(EventType.KILL_FEED)
    async def kill_handler(event: Event):
        log.info(f"Kill event: \"{event.content}\"")

    @staticmethod
    @EventListener.listen(EventType.CHAT)
    async def chat_handler(event: Event):
        log.info(f"Chat event: \"{event.content}\"")

    @staticmethod
    @EventListener.listen(EventType.LOGIN)
    async def join_handler(event: Event):
        log.info(f"Player join event: \"{event.content}\"")

    @staticmethod
    @EventListener.listen(EventType.MATCH_STATE)
    async def match_handler(event: Event):
        log.info(f"Match event: \"{event.content}\"")

    @staticmethod
    @EventListener.listen(EventType.SCORE_FEED)
    async def score_handler(event: Event):
        log.info(f"Score event: \"{event.content}\"")

    @staticmethod
    @EventListener.listen(EventType.PUNISHMENT)
    async def punishment_handler(event: Event):
        log.info(f"Punishment event: \"{event.content}\"")


__all__ = [
    "LogEvents"
]
