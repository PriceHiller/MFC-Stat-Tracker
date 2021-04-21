import logging
import os
import json

from dataclasses import dataclass

from tracker import Base

from tracker.events import EventListener
from tracker.events import Event
from tracker.mordhau_events.type import EventType

from tracker.apirequest import APIRequest

log = logging.getLogger(__name__)


@dataclass
class ChatCommand:
    playfab_id: str
    player_name: str
    command: str
    message: str


class Commands:

    @staticmethod
    async def register(command: ChatCommand):
        registration_dict = {
            "playfab_id": command.playfab_id,
            "player_name": command.player_name,
        }

        response = await APIRequest.post("/player/create", data=registration_dict)
        if response.status == 409:
            await Base.connection(f"say You are already registered")
        elif response.status == 200:
            await Base.connection(f"say Registered {command.player_name} with id "
                                  f"{response.json['extra'][0]['player_id']}")


class ChatEvents:
    prefix = os.getenv("CHAT_PREFIX", default="-")

    @staticmethod
    @EventListener.listen(EventType.CHAT)
    async def base_chat_handler(event: Event):
        split_event = event.content.split(",")
        playfab_id = split_event[0]
        player_name = split_event[1]
        message = "".join(split_event[2].split(") ")[1:])
        command = ChatCommand(playfab_id.strip(), player_name.strip(), message[1:].strip().casefold(), message.strip())
        if not event.content or not message[0] == ChatEvents.prefix:
            return
        log.info(f"Command attempt made: {command}")
        if command.command == "register":
            await Commands.register(command)


