"""
Example Listener Setup
======================
>>> # __init__.py
>>> from tracker.events import EventListener
>>> from tracker.mordhau_events.type import BaseMordhauEvent
>>>
>>> class Test:
>>>
>>>     @staticmethod
>>>     @EventListener.listen(BaseMordhauEvent.MATCH_STATE)
>>>     async def another_state(event):
>>>         print("HIT")
>>>
>>> # Then export to dunder-all in this __init__.py ...
>>> __all__ = ["Test"]
"""

from tracker.mordhau_events.Logging import LogEvents
from tracker.mordhau_events.commands.register import Registration


class RegisteredEvents:
    log_events = LogEvents
    registration = Registration


__all__ = [
    "RegisteredEvents"
]
