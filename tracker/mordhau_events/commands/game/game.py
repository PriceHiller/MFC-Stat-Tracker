import logging
import os
import asyncio


from aiorcon import RCON

from avents import listen
from avents import Event

from tracker.mordhau_events import MordhauType

from tracker.mordhau_events.commands import CommandEventType
from tracker.mordhau_events.commands import CommandListener
from tracker.mordhau_events.commands import CommandEvent

from tracker import Base
from tracker.apirequest import APIRequest

from tracker.mordhau_events.commands.game import Match
from tracker.mordhau_events.commands.game import Set
from tracker.mordhau_events.commands.game import Round
from tracker.mordhau_events.commands.game import Player
from tracker.mordhau_events.commands.game import Team

log = logging.getLogger(__name__)


class Game:

    admins = os.getenv("MATCH_ADMINS", default=None)
    if not admins:
        log.warning(f"There are no admins (MATCH_ADMINS) set in the environment. It should be a comma delimited list "
                    f"of playfab ids.")
        admins = []
    else:
        admins = admins.split(",")

    valid_maps = os.getenv("MATCH_VALID_MAPS", default=None)
    if not valid_maps:
        log.warning(f"There are no valid maps (MATCH_VALID_MAPS) set in the environment. It should be a comma "
                    f"delimited list of Mordhau map names, e.g. skm_moshpit, ...")
        valid_maps = []
    else:
        valid_maps = valid_maps.split(",")

    match = None
    sets = []
    current_set = None
    rounds = []
    current_round = None
    map_queue = []
    recording = False


    @classmethod
    async def check_admin_perm(cls, playfab_id) -> bool:
        """Returns true if the given playfab id is in the admins environment list"""
        if playfab_id in cls.admins:
            return True
        return False

    @staticmethod
    @CommandListener.listen(CommandEventType.MATCH_SETUP)
    async def match_setup_hook(event: CommandEvent):
        await Game.match_setup(event)

    @classmethod
    async def match_setup(cls, command: CommandEvent):
        # connection = await RCON.create(Base.ip, Base.port, Base.)

        if not await cls.check_admin_perm(command.playfab_id):
            await Base.connection(f"say You are not permitted to run this command")
            return

        example_message = f"say \nAn example would be:\n" \
                          f"- match start Vanquish, Racecar, skm_moshpit, skm_contraband, skm_antheum,..."

        if len(command.content) <= 2:  # if the len is less than or equal then no arguments have been supplied
            await Base.connection(f"say \nThe parameter args for \"match start\" are:\n"
                                  f"    - team1 name\n"
                                  f"    - team2 name\n"
                                  f"    - *maps\n")
            await Base.connection(example_message)
            return

        command_args = " ".join(command.content[2:])  # this removes the command and only takes in arguments

        if "," not in command_args:
            await Base.connection(f"say Invalid usage!")
            await Base.connection(example_message)
            return

        split_args = [arg.strip() for arg in command_args.split(",")]

        if len(split_args) < 3:
            await Base.connection(f"More args must be passed, only received: {', '.join(split_args)}")
            await Base.connection(example_message)
            return

        maps = split_args[2:]

        for map in maps:
            if map not in cls.valid_maps:
                await Base.connection(f"The map {map} is not a valid map!")
                return

        cls.map_queue = maps

        team1 = await Team.get_team_by_name(team_name=split_args[0])

        if team1.status == 404:
            await Base.connection(f"say Could not find the team: {split_args[0]}")
            return

        if team1.status != 200:
            await Base.connection(f"say Unable to retrive data from the API for {split_args[0]}")
            return

        team2 = await Team.get_team_by_name(team_name=split_args[1])

        if team2.status == 404:
            await Base.connection(f"say Could not find the team: {split_args[1]}")
            return

        if team2.status != 200:
            await Base.connection(f"say Unable to retrive data from the API for {split_args[1]}")
            return

        team1 = Team(team1.json["id"], split_args[0])
        team2 = Team(team2.json["id"], split_args[1])

        cls.match = Match(team1, team2)

        await Base.connection(f"say Setup the match with the following params:\n")
        map_rotation_formatted = f"\n- ".join(cls.map_queue)
        await Base.connection(f"say Params:\n"
                              f"Red team: `{team1.name}`\n"
                              f"Blue team: `{team2.name}`\n\n"
                              f"Map rotation:\n"
                              f"- {map_rotation_formatted}")

    @staticmethod
    @CommandListener.listen(CommandEventType.MATCH_START)
    async def _start_match_hook(event: CommandEvent):
        if Game.match is None:
            await Base.connection(f"say It appears that the match has not been setup. Please run `match setup`!")
            return
        await Game.next_set()


    @classmethod
    async def next_set(cls):
        if len(cls.map_queue) > 0:
            next_map = cls.map_queue.pop()
            next_map = cls.map_queue[0]
            del cls.map_queue[0]
            new_set = Set(cls.match, next_map)
            if cls.current_set:
                cls.sets.append(cls.current_set)
            cls.current_set = new_set
            await Base.connection(f"say Moving to next map: `{next_map}`")
            await asyncio.sleep(3)
            await Base.connection(f"changelevel {next_map}")
            cls.recording = True
            #await asyncio.sleep(15)
            await Base.connection(f"say Teams:\n"
                                  f"Red:  `{cls.match.team1.name}`\n"
                                  f"Blue: `{cls.match.team2.name}")

    @classmethod
    async def end_match(cls):
        ...
