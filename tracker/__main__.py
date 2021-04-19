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

from tracker import Base

log = logging.getLogger(__name__)


def main():
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(Base.run())
    except KeyboardInterrupt:
        log.info("Exiting...")


if __name__ == "__main__":
    main()
