from tracker.mordhau_events.Logging import LogEvents
from tracker.mordhau_events.commands.register import Registration
from tracker.mordhau_events.commands.game.game import Game


class RegisteredEvents:
    log_events = LogEvents
    registration = Registration
    mfc_game = Game