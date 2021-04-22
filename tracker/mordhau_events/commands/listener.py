import enum
import os
import logging

from dataclasses import dataclass

from tracker.events import Event
from tracker.events import EventListener

from tracker.mordhau_events.type import EventType

log = logging.getLogger(__name__)


class CommandEventType(enum.Enum):
    REGISTER: str = "register"
    MATCH: str = "match"
    MATCH_RESTART: str = "match restart"

    def __str__(self):
        return self.value


class CommandListener(EventListener):
    _listening_events = {}


@dataclass
class ChatCommand:
    playfab_id: str
    player_name: str
    command: str
    message: str


class ChatCommandHandler:
    prefix = os.getenv("CHAT_PREFIX", default="-")

    @staticmethod
    @EventListener.listen(EventType.CHAT)
    async def base_chat_handler(event: Event):
        split_event = event.content.split(",")
        playfab_id = split_event[0]
        player_name = split_event[1]
        message = "".join(split_event[2].split(") ")[1:])
        command = ChatCommand(playfab_id.strip(), player_name.strip(), message[1:].strip().casefold(), message.strip())
        log.info(f"Command attempt made: {command}")
        await CommandListener.parse_event(Event(event.name, command))
