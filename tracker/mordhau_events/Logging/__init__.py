import logging

from avents import Event
from tracker.mordhau_events import MordhauListener
from tracker.mordhau_events import MordhauType


log = logging.getLogger(__name__)


class LogEvents:

    @staticmethod
    @MordhauListener.listen(MordhauType.KILL_FEED)
    async def kill_handler(event: Event):
        log.info(f"Kill event: \"{event.content}\"")

    @staticmethod
    @MordhauListener.listen(MordhauType.CHAT)
    async def chat_handler(event: Event):
        log.info(f"Chat event: \"{event.content}\"")

    @staticmethod
    @MordhauListener.listen(MordhauType.LOGIN)
    async def join_handler(event: Event):
        log.info(f"Player join event: \"{event.content}\"")

    @staticmethod
    @MordhauListener.listen(MordhauType.MATCH_STATE)
    async def match_handler(event: Event):
        log.info(f"Match event: \"{event.content}\"")

    @staticmethod
    @MordhauListener.listen(MordhauType.SCORE_FEED)
    async def score_handler(event: Event):
        log.info(f"Score event: \"{event.content}\"")

    @staticmethod
    @MordhauListener.listen(MordhauType.PUNISHMENT)
    async def punishment_handler(event: Event):
        log.info(f"Punishment event: \"{event.content}\"")


__all__ = [
    "LogEvents"
]
