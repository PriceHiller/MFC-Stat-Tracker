import logging

from . import CommandEventType
from . import CommandListener
from . import CommandEvent

from tracker import rcon_command
from tracker.apirequest import APIRequest

log = logging.getLogger(__name__)


class Registration:

    @staticmethod
    @CommandListener.listen(CommandEventType.REGISTER)
    async def register(command: CommandEvent):
        registration_dict = {
            "playfab_id": command.playfab_id,
            "player_name": command.player_name,
        }

        response = await APIRequest.post("/player/create", data=registration_dict)
        if response.status == 409:
            await rcon_command(f"say Attempted to register {command.player_name}, but they were already registered.")
        elif response.status == 200:
            await rcon_command(f"say Registered {command.player_name} with id "
                               f"{response.json['extra'][0]['player_id']}")
        else:
            await rcon_command(f"say Unable to register {command.player_name}! Response status: {response.status}. "
                               f"The API may be down.")
            log.error(f"Unable to register: {registration_dict}, response status: {response.status}")
