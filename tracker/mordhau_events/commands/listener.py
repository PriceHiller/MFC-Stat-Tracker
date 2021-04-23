import os
import logging

from dataclasses import dataclass

from avents import BaseEventType
from avents import Event
from avents import EventListener
from avents import listen

from tracker.mordhau_events.type import BaseMordhauEvent

log = logging.getLogger(__name__)


class CommandEventType(BaseEventType):
    REGISTER: str = "register"
    MATCH: str = "match"
    MATCH_RESTART: str = "match restart"


class CommandListener(EventListener):
    ...


@dataclass
class CommandEvent(Event):
    playfab_id: str
    player_name: str


class ChatCommandHandler:
    prefix = os.getenv("CHAT_PREFIX", default="-")

    @staticmethod
    @listen(BaseMordhauEvent.CHAT)
    async def base_chat_handler(event: Event):
        split_event = event.content.split(",")
        playfab_id = split_event[0]
        player_name = split_event[1]
        message = "".join(split_event[2].split(") ")[1:]).strip()
        if message[0] != ChatCommandHandler.prefix:
            return

        command_content = []
        command_name = ""

        for command_event in CommandEventType: # Ensure that the command passed is actually a KNOWN command
            command_event = str(command_event)
            if command_event in message.casefold():
                command_name = command_event
                command_message = message[1:]
                command_message.replace(command_event, "")
                command_content = command_message.split(" ")

        command = CommandEvent(
            command_name,
            command_content,
            playfab_id.strip(),
            player_name.strip(),
        )
        log.info(f"Command attempt made: {command}")
        await CommandListener.parse(command)
