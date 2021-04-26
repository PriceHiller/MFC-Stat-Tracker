import logging
from dataclasses import dataclass

from tracker import Base

from tracker.apirequest import APIRequest
from tracker.apirequest import APIError

from tracker.mordhau_events.commands import CommandListener
from tracker.mordhau_events.commands import CommandEvent

log = logging.getLogger(__name__)


@dataclass
class Player:
    """A dataclass that loosely defines a player according to the MFC API"""
    playfab_id: str
    api_id: [str, None]
    name: str
    score: int
    kills: int
    assists: int
    deaths: int


class Team:

    def __init__(self, team_id, name):
        self.id = team_id
        self.name = name
        self.players: dict[str, Player] = {}

    async def add_player(self, player: Player):
        """This adds a player to the team and registers them with the API if they are not already tracked."""
        if self.players.get(player.playfab_id):
            return

        api_player = await APIRequest.get(f"/player/playfab-id?playfab_id={player.playfab_id}")

        if api_player.status != 200:
            # This registers a player with the API in the scenario we were unable to get them
            register_event = CommandEvent("register", None, player.playfab_id, player.name)
            await CommandListener.parse(register_event)
        api_player = await APIRequest.get(f"/player/playfab-id?playfab_id={player.playfab_id}")
        if api_player.status != 200:
            # In the scenario we were unable to find them after registration we log the event and notify the match
            await Base.connection(f"Say something has gone wrong, was unable to find player {player.name}, "
                                  f"but they should already be registered!")
            log.error(f"Was unable to find player \"{player.name}\", playfab: \"{player.playfab_id}\" when they "
                      f"should've already been registered")
            return
        player_json = api_player.json
        player.api_id = player_json["id"]
        self.players[player.playfab_id] = player

    @staticmethod
    async def get_team_by_name(team_name):
        team_data = await APIRequest.get(f"/team/name?team_name={team_name}")
        return team_data


class Match:

    def __init__(self, red_team: Team, blue_team: Team):
        self.team1 = red_team
        self.team2 = blue_team
        self.api_data = None
        self.id = None

    async def __aenter__(self):
        new_match = await APIRequest.post(
            "/match/create-match",
            data={
                "team1_id": self.team1.id,
                "team2_id": self.team2.id
            })
        if new_match.status != 200:
            log.error(f"Unable to create a new match, status: \"{new_match.status}\", content: \"{new_match.json}\"")
            raise APIError(new_match.status, new_match.json)
        self.api_data = new_match.json
        self.id = self.api_data["extra"][0]["match_id"]


class Set:

    def __init__(self, match: Match, map: str):
        self.match = match
        self.map = map
        self.api_data = None
        self.id = None

    async def __aenter__(self, map: str):
        new_set = await APIRequest.post("/set/create")
        if new_set.status != 200:
            log.error(f"Unable to create a new set, status: \"{new_set.status}\", content: \"{new_set.json}\"")
            raise APIError(new_set.status, new_set.json)

        self.api_data = new_set.json
        self.id = self.api_data["extra"][0]["set_id"]


class Round:

    def __init__(self, set: Set):
        self.set = set
        self.team1 = set.match.team1
        self.team2 = set.match.team2
        self.api_data = None
        self.id = None

    async def __aenter__(self):
        new_round = await APIRequest.post(f"/round/create-round")
        if new_round.status != 200:
            log.error(f"Unable to create a new round, status: \"{new_round.status}\", content: \"{new_round.json}\"")
            raise APIError(new_round.status, new_round.json)
        self.api_data = new_round.json
        self.id = self.api_data["extra"][0]["set_id"]
