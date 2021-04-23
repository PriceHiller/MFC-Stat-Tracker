import asyncio
import time
import os
import sys
import logging
from pathlib import Path
from logging import config

import aiorcon.messages
import yaml
from aiorcon import RCON
from dotenv import load_dotenv

from avents import parse
from avents import Event

from tracker.mordhau_events.type import BaseMordhauEvent

log = logging.getLogger(__name__)


# Some paths set that may be useful elsewhere in the program
root_path = Path(__file__).parent
environment_path = root_path.parent / ".env"


# Load the environment variables
if environment_path.exists():
    load_dotenv(environment_path)
else:
    log.critical("A .env file is not defined in the root directory, ensure your variables are exported in the "
                 "environment")
    sys.exit(1)


def setup_logging() -> None:
    """Load the log yaml config file"""
    try:
        if log_config_path := os.getenv("LOG_CONFIG_PATH", default=None):
            log_config_path = Path(log_config_path)
        else:
            log_config_path = root_path / "log_config.yaml"

        with open(log_config_path) as f:
            log_config = yaml.safe_load(f)
    except FileNotFoundError as error:
        print(f"Could not find your log config at: {str(error).split(' ')[-1]}")
        return

    config.dictConfig(log_config)


class Base:
    ip = os.getenv("RCON_IP", default=None)  # The ip for the RCON connection
    if not ip:
        log.critical(f"A(n) IP address (RCON_IP) was not set in the environment: \"{environment_path}\"")
        sys.exit(128)
    port = os.getenv("RCON_PORT", default=None)  # The port for the RCON connection
    if not port:
        log.critical(f"A(n) RCON port (RCON_PORT) was not set in the environment: \"{environment_path}\"")
        sys.exit(128)
    try:
        port = int(port)
    except ValueError:
        log.critical(f"The RCON port was not a valid port number, should be a WHOLE number (e.g. 123)!")
        sys.exit(128)
    password = os.getenv("RCON_PASSWORD", default=None)  # The password for the RCON connection
    if not port:
        log.critical(f"A(n) RCON password (RCON_PASSWORD) was not set in the environment: \"{environment_path}\"")
        sys.exit(128)

    connection: RCON  # The uncreated RCON object, created vie the run method

    @classmethod
    async def read(cls, buffer: aiorcon.messages.ResponseBuffer, keep_alive_prod: float = 30):
        """Listen and yield events from the RCON connection"""
        keep_alive_sent = time.time()
        while True:
            if buffer.responses:
                item = buffer.pop()
                yield item
            if (time.time() - keep_alive_sent) > keep_alive_prod:
                log.debug(f"Sending keep alive")
                try:
                    await cls.connection("info")
                except Exception:
                    log.exception(f"Sending keep alive failed.")
                keep_alive_sent = time.time()
            await asyncio.sleep(1)

    @staticmethod
    def format_mordhau_bytes(input: bytes) -> list[str]:
        """Removes all non-ascii bytes from input and returns a split list of strings split on :"""
        string = bytes(input).split(b"\x00").pop(0).decode("ascii", errors="ignore")
        partials = [_.strip() for _ in string.replace("  ", "").replace("\t", "").strip().split(":")]

        # string = bytes(input).split(b"\x00").pop(0).decode("ascii", errors="ignore").encode("ascii", errors="ignore").decode()
        # partials = string.replace("  ", "").replace("\t", "").split(":")

        return partials

    @classmethod
    async def run(cls):
        """Run the program"""
        setup_logging()
        try:
            cls.connection: RCON = await RCON.create(
                cls.ip,
                cls.port,
                cls.password,
                asyncio.get_event_loop(),
                multiple_packet=False,
                timeout=20
            )
        except ConnectionRefusedError as error:
            log.critical(f"Could not connect to RCON: \"{cls.ip}:{cls.port}\", connection was refused")
            return
        # Imported after a connection is established and env vars are loaded
        from tracker.mordhau_events import RegisteredEvents

        log.info("Connected to: " + (" - ".join([line for line in (await cls.connection("info")).split("\n")])))
        log.info(f"RCON connected to {cls.ip}:{cls.port}")
        raw_rcon = logging.getLogger("raw_rcon")  # This defines raw rcon output without any logging formatting
        log.info((await cls.connection("listen allon")).strip())
        async for event in cls.read(cls.connection.protocol._buffer):
            event: aiorcon.messages.RCONMessage
            raw_rcon.info(event.body)  # log the raw RCON output
            log.debug(f"Received RCON emission: {event.body}")

            # Split on NULL character, line terminator. This catches some scenarios in which RCON combines two message
            # into one with a NULL character between them.
            for event_line in event.body.split(b"\\x00"):
                partials = cls.format_mordhau_bytes(event_line)
                log.debug(f"Received event: \"{':'.join(partials)}\"")
                await parse(Event(name=partials[0], content=":".join(partials[1:])))

