import enum


class EventType(enum.Enum):
    LOGIN: str = "Login"
    PUNISHMENT: str = "Punishment"
    MATCH_STATE: str = "MatchState"
    SCORE_FEED: str = "Scorefeed"
    KILL_FEED: str = "Killfeed"
    CHAT: str = "Chat"

    def __str__(self):
        return self.value
