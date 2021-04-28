from avents import EventListener
from avents import listen
from avents import Event
from avents import BaseEventType


class MordhauListener(EventListener):
    ...


class MordhauType(BaseEventType):
    LOGIN: str = "Login:"
    PUNISHMENT: str = "Punishment:"
    MATCH_STATE: str = "MatchState:"
    SCORE_FEED: str = "Scorefeed:"
    KILL_FEED: str = "Killfeed:"
    CHAT: str = "Chat:"


@listen("RCON")
async def mordhau_event_parser(event: Event):
    for mord_type in MordhauType:
        mord_type = str(mord_type)
        if mord_type in event.content:
            split_content = event.content.split(mord_type)
            for rcon_content in split_content:
                if rcon_content:
                    await MordhauListener.parse(Event(str(mord_type), rcon_content.strip()))
