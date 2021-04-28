import logging

from tracker import rcon_command

from avents import Event
from tracker.mordhau_events import MordhauListener
from tracker.mordhau_events import MordhauType


log = logging.getLogger(__name__)


class LogEvents:

    @staticmethod
    @MordhauListener.listen(*[mord_type for mord_type in MordhauType])
    async def log_event(event: Event):
        log.info(f"{event.name} \"{event.content}\"")

__all__ = [
    "LogEvents"
]
