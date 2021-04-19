import asyncio

from tracker import Base
from tracker.events.test import _asdf

def main():
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    loop.run_until_complete(Base.run())


if __name__ == "__main__":
    main()
