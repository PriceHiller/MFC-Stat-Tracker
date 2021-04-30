import logging
import os
import asyncio
import re

from tracker.mordhau_events import MordhauType

from tracker.mordhau_events import MordhauListener

from tracker.mordhau_events.commands import CommandEventType
from tracker.mordhau_events.commands import CommandListener
from tracker.mordhau_events.commands import CommandEvent

from tracker import rcon_command
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

    match: [Match, None] = None
    current_set: [Set, None] = None
    current_round: [Round, None] = None
    map_queue: list[str] = []
    recording: bool = False
    players: dict[str, Player] = {}

    @classmethod
    async def check_admin_perm(cls, playfab_id) -> bool:
        """Returns true if the given playfab id is in the admins environment list"""
        if playfab_id in cls.admins:
            return True
        return False

    @staticmethod
    @CommandListener.listen(CommandEventType.MATCH_SETUP)
    async def _match_setup_hook(event: CommandEvent):
        await Game.match_setup(event)

    @classmethod
    async def match_setup(cls, command: CommandEvent):
        if not await cls.check_admin_perm(command.playfab_id):
            await rcon_command(f"say You are not permitted to run this command")
            return

        if Game.match:
            await Game.end_match()

        example_message = f"say \nAn example would be:\n" \
                          f"- match start Vanquish, Racecar, skm_moshpit, skm_contraband, skm_antheum,..."

        if len(command.content) <= 2:  # if the len is less than or equal then no arguments have been supplied
            await rcon_command(f"say \nThe parameter args for \"match start\" are:\n"
                               f"    - team1 name\n"
                               f"    - team2 name\n"
                               f"    - *maps\n")
            await rcon_command(example_message)
            return

        command_args = " ".join(command.content[2:])  # this removes the command and only takes in arguments

        if "," not in command_args:
            await rcon_command(f"say Invalid usage!")
            await rcon_command(example_message)
            return

        split_args = [arg.strip() for arg in command_args.split(",")]

        if len(split_args) < 3:
            await rcon_command(f"More args must be passed, only received: {', '.join(split_args)}")
            await rcon_command(example_message)
            return

        maps = split_args[2:]

        for map in maps:
            if map not in cls.valid_maps:
                await rcon_command(f"The map {map} is not a valid map!")
                return

        cls.map_queue = maps

        team1 = await Team.get_team_by_name(team_name=split_args[0])

        if team1.status == 404:
            await rcon_command(f"say Could not find the team: {split_args[0]}")
            return

        if team1.status != 200:
            await rcon_command(f"say Unable to retrive data from the API for {split_args[0]}")
            return

        team2 = await Team.get_team_by_name(team_name=split_args[1])

        if team2.status == 404:
            await rcon_command(f"say Could not find the team: {split_args[1]}")
            return

        if team2.status != 200:
            await rcon_command(f"say Unable to retrive data from the API for {split_args[1]}")
            return

        team1 = Team(team1.json["id"], split_args[0])
        team2 = Team(team2.json["id"], split_args[1])

        cls.match = Match(team1, team2)
        await cls.match.ainit()

        await rcon_command(f"say Setup the match with the following params:\n")
        map_rotation_formatted = f"\n- ".join(cls.map_queue)
        await rcon_command(f"say Params:\n"
                           f"Red team: {team1.name}\n"
                           f"Blue team: {team2.name}\n\n"
                           f"Map rotation:\n"
                           f"- {map_rotation_formatted}")

    @staticmethod
    @CommandListener.listen(CommandEventType.MATCH_START)
    async def _start_match_hook(event: CommandEvent):
        if not await Game.check_admin_perm(event.playfab_id):
            await rcon_command(f"say You are not permitted to run this command")
            return

        if Game.match is None:
            await rcon_command(f"say It appears that the match has not been setup. Please run `match setup`!")
            return
        await Game.next_set()

    @staticmethod
    @CommandListener.listen(CommandEventType.MATCH_PAUSE)
    async def pause_match(event: CommandEvent):
        if not await Game.check_admin_perm(event.playfab_id):
            await rcon_command(f"say You are not permitted to run this command")
            return
        if Game.match:
            Game.recording = False
            await rcon_command(f"say Paused the match.")
        else:
            await rcon_command(f"say A match is not currently ongoing.")

    @staticmethod
    @CommandListener.listen(CommandEventType.MATCH_RESUME)
    async def resume_match(event: CommandEvent):
        if not await Game.check_admin_perm(event.playfab_id):
            await rcon_command(f"say You are not permitted to run this command")
            return
        if Game.match:
            Game.recording = True
            await rcon_command(f"say Resumed the match.")
        else:
            await rcon_command(f"say A match is not currently ongoing.")

    @staticmethod
    @CommandListener.listen(CommandEventType.MATCH_NEXT)
    async def match_next_command(event: CommandEvent):
        if not await Game.check_admin_perm(event.playfab_id):
            await rcon_command(f"say You are not permitted to run this command")
            return
        if not Game.match:
            await rcon_command(f"say A match is not currently ongoing.")
            return
        await Game.next_set()

    @classmethod
    async def next_set(cls):
        if len(cls.map_queue) > 0:
            next_map = cls.map_queue.pop(0)
            new_set = Set(cls.match, next_map)
            await new_set.ainit()
            cls.current_set = new_set
            new_round = Round(new_set)
            cls.current_round = new_round
            await rcon_command(f"say Moving to next map: `{next_map}`")
            await asyncio.sleep(3)
            await rcon_command(f"changelevel {next_map}")
            cls.recording = True
            await asyncio.sleep(15)
            await rcon_command(f"say Teams:\n"
                               f"Red: {cls.match.team1.name}, score: {cls.match.team1_score}\n"
                               f"Blue: {cls.match.team2.name}, score:  {cls.match.team2_score}")
        else:
            await cls.end_match()

    @staticmethod
    @CommandListener.listen(CommandEventType.MATCH_END)
    async def match_end_command(event: CommandEvent):
        if not await Game.check_admin_perm(event.playfab_id):
            await rcon_command(f"say You are not permitted to run this command")
            return
        await Game.end_match()

    @classmethod
    async def end_match(cls):
        if cls.match:
            response = await APIRequest.post(f"/match/calculate-match-elo?match_id={cls.match.id}")
            if response.status != 200:
                await rcon_command(f"say Could not calculate elo, response status: {response.status}. Keeping match "
                                   f"alive and pausing it.")
                log.error(f"Could not calculate elo, response status: {response.status}")
                cls.recording = False
                return
            match_id = cls.match.id
            cls.match = None
            cls.map_queue = []
            cls.current_set = None
            cls.current_round = None
            cls.recording = False
            await rcon_command(f"say Match ended, id: {match_id}")
            return

    @staticmethod
    @MordhauListener.listen(MordhauType.SCORE_FEED)
    async def _round_end_hook(event: CommandEvent):
        await Game.process_round_end(event)

    @classmethod
    async def process_round_end(cls, event: CommandEvent):
        if not cls.recording:
            return
        search = re.findall(".\d+", event.content.split(":")[-1].strip())
        try:
            team_num = int(search[1].strip())
            if team_num < 0:
                return
            team_initial_score = int(search[1].strip())
            team_new_score = int(search[3].strip())
        except IndexError:
            return
        except ValueError:
            return
        if team_initial_score == team_new_score:
            return
        current_map = (await rcon_command("info")).casefold().strip().split("map: ")[-1]
        if current_map not in cls.current_set.map.strip().casefold():
            await rcon_command(f"say Attempted to gather data for the last round, but it was not on the correct map. "
                               f"The expected map that data is being gathered for is {cls.current_set.map}!")
            return
        log.info(f"Round End processing")
        scoreboard = (await rcon_command("scoreboard")).split("\n")
        players = []
        for scoreboard_player in scoreboard:
            if not scoreboard_player.strip():
                continue
            player_split = scoreboard_player.split(", ")
            team_num = int(player_split[2])

            if team_num < 0:
                continue

            playfab = player_split[0]
            name = player_split[1]
            score = int(player_split[4])
            kills = int(player_split[5])
            deaths = int(player_split[6])
            assists = int(player_split[7])

            if team_num == 0:
                team_id = cls.match.team1.id
                cls.match.team1_score += 1
                await cls.current_round.create(True, False)
            else:
                team_id = cls.match.team2.id
                cls.match.team2_score += 1
                await cls.current_round.create(False, True)

            player = Player(playfab, None, team_id, cls.current_round.id, team_num, name, score, kills, assists, deaths)
            await player.get_api_id()
            registered_player = cls.players.get(player.playfab_id, None)
            if not registered_player:
                cls.players[player.playfab_id] = player
            else:
                player.kills -= registered_player.kills
                player.score -= registered_player.score
                player.assists -= registered_player.assists
                player.deaths -= registered_player.deaths
            players.append(player)

        api_round_players = {"round_players": [vars(player) for player in players]}
        response = await APIRequest.post("/round/create-round-players", data=api_round_players)

        if response.status == 200:
            await rcon_command(f"say Saved data for the last round, id: {cls.current_round.id}")
            cls.current_round = Round(cls.current_set)
        else:
            await rcon_command(f"Unable to save data for the last round, status code: {response.status}")
            log.error(f"Unable to save data for a ended tracked round, data sent: \"{api_round_players}\", "
                      f"received response: \"{response.status}\", \"{response.json}\"")
