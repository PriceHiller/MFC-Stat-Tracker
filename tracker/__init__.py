import os
import sys
import logging
from pathlib import Path
from logging import config

import yaml
from srcds.rcon import RconConnection
from dotenv import load_dotenv

from tracker.events import EventListener
from tracker.events import Event

log = logging.getLogger(__name__)
root_path = Path(__file__).parent
environment_path = root_path.parent / ".env"

if environment_path.exists():
    load_dotenv(environment_path)
else:
    log.critical("A .env file is not defined in the root directory, ensure your variables are exported in the "
                 "environment")
    sys.exit(1)


def setup_logging() -> None:
    try:
        if log_config_path := os.getenv("log_config_path", default=None):
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
    ip = os.getenv("RCON_IP", default=None)
    if not ip:
        log.critical(f"A(n) IP address (RCON_IP) was not set in the environment: \"{environment_path}\"")
        sys.exit(1)
    port = os.getenv("RCON_PORT", default=None)
    if not port:
        log.critical(f"A(n) RCON port (RCON_PORT) was not set in the environment: \"{environment_path}\"")
        sys.exit(1)
    try:
        port = int(port)
    except ValueError:
        log.critical(f"The RCON port was not a valid port number, should be a WHOLE number (e.g. 123)!")
        sys.exit(1)
    password = os.getenv("RCON_PASSWORD", default=None)
    if not port:
        log.critical(f"A(n) RCON password (RCON_PASSWORD) was not set in the environment: \"{environment_path}\"")
        sys.exit(1)

    try:
        connection = RconConnection(ip, port=port, password=password,
                                    single_packet_mode=True)
        log.info(f"Connected to RCON: \"{ip}:{port}\"")
    except Exception as error:
        log.exception("Could not connect to the server")
        sys.exit(1)

    @classmethod
    async def read(cls):
        while True:
            yield cls.connection.read_response().body

    @staticmethod
    def format_mordhau_bytes(input: bytes) -> list[str]:
        string = bytes(input[:-3]).decode("ascii", errors="ignore").encode("ascii", errors="ignore")
        partials = string.decode(encoding="UTF-8").strip().replace("  ", " ").replace("\t", " ").split(":")
        return partials

    @classmethod
    async def run(cls):
        setup_logging()
        log.info(f"RCON connected to {cls.ip}:{cls.port}")
        log.info("RCON info: " +
                 " - ".join(":".join(cls.format_mordhau_bytes(cls.connection.exec_command("info"))).split("\n"))
                 )
        cls.connection.exec_command("listen allon")
        async for event in cls.read():
            log.debug(f"Received RCON emission: {event}")
            partials = cls.format_mordhau_bytes(event)
            log.info(f"Received event: \"{':'.join(partials)}\"")
            await EventListener.parse_event(Event(name=partials[0], content=",".join(partials[1:]).strip()))
