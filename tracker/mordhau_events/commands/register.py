from . import command_listen
from . import CommandEventType
from . import Event
from . import ChatCommand

from tracker import Base
from tracker.apirequest import APIRequest


class Registration:

    @staticmethod
    @command_listen(CommandEventType.REGISTER)
    async def register(event: Event):
        command: ChatCommand = event.content
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

