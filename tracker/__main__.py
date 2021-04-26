"""
External, Packaged Use
----------------------
    >>> from package.module.name import *

Debugging
=========
asyncio (Standard Library)
    >>> loop.set_debug(True)
"""

import asyncio
import logging
import sys

from tracker import Base

log = logging.getLogger(__name__)


def main(*args):
    loop = asyncio.get_event_loop()

    lower_args = [arg.casefold() for arg in args[0]]

    if "--debug" in lower_args or "-d" in lower_args:
        loop.set_debug(True)
        print("Enabled debug for the async loop")

    try:
        loop.run_until_complete(Base.run())
    except KeyboardInterrupt:
        log.info("Exiting...")


if __name__ == "__main__":
    main(sys.argv)
