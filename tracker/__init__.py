import os
import sys
import logging
import subprocess
import asyncio
from pathlib import Path
from logging import config

import yaml
from srcds.rcon import RconConnection
from dotenv import load_dotenv

from avents import parse
from avents import Event

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
    except ConnectionRefusedError:
        log.error(f"Connection was refused to \"{ip}:{port}\", verify that your connection info is correct and that "
                  f"the server is up.")
        sys.exit(1)
    except Exception as error:
        log.exception("Could not connect to the server")
        sys.exit(1)

    @classmethod
    async def read(cls, read_log=False):
        if read_log:
            raw_rcon_log = root_path.parent / "raw_rcon.log"
            log.info(f"Reading the log data in \"{str(raw_rcon_log)}\"")
            await asyncio.sleep(3)  # Sleep so we have time to read the output of the log message above
            if not raw_rcon_log.exists():
                log.error(
                    f"Expected the log \"{str(raw_rcon_log)}\" but it did not exist! The `read log` flag requires "
                    f"that file to read data from!")
                return
            with open(raw_rcon_log, "r") as f:
                for line in f.readlines():
                    yield line[1:-1].encode()
        else:
            while True:
                yield cls.connection.read_response().body

    @staticmethod
    def format_mordhau_bytes(input: bytes) -> str:
        """Removes all non-ascii bytes from input and returns a split list of strings split on :"""
        string = bytes(input).split(b"\x00").pop(0).decode("ascii", errors="ignore")
        return string

        # string = bytes(input).split(b"\x00").pop(0).decode("ascii", errors="ignore").encode("ascii", errors="ignore").decode()
        # partials = string.replace("  ", "").replace("\t", "").split(":")
        #
        # return partials

    @classmethod
    async def run(cls, *args):
        setup_logging()
        log.info(f"RCON connected to {cls.ip}:{cls.port}")
        log.info("RCON info: " +
                 " - ".join("".join(cls.format_mordhau_bytes(cls.connection.exec_command("info"))).split("\n"))
                 )
        cls.connection.exec_command("listen allon")
        await cls.rcon_command(f"say RCON Data Ingester Online, Version {open(root_path.parent / 'VERSION').read()}.\n"
                               f"Written by Price Hiller (Sbinalla), contributors:\n"
                               f"   - Jacob Sanders (Null Byte)\n"
                               f"   - Clinically Lazy (Clinically Lazy)")
        from tracker.mordhau_events.event_registration import RegisteredEvents

        raw_rcon = logging.getLogger("raw_rcon")

        if "--read-log" in args or "-r" in args:
            read_log = True
        else:
            read_log = False
        async for event in cls.read(read_log=read_log):
            log.debug(f"Received RCON emission: {event}")
            raw_rcon.info(event)

            # Split on NULL character, line terminator. This catches some scenarios in which RCON combines two message
            # into one with a NULL character between them.
            for split_event in event.split(rb"\x00"):
                partials = cls.format_mordhau_bytes(split_event)
                log.debug(f"Received event: \"{partials.strip()}\"")
                await parse(Event(name="RCON", content=partials))

    @classmethod
    async def rcon_command(cls, command: str) -> str:
        log.debug(f"Issued RCON command: \"{command.strip()}\"")
        process = await asyncio.create_subprocess_shell(
            f"RCON --Server {cls.ip} --Port {cls.port} --Password {cls.password} -c \"{command}\"",
            shell=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        data = (await process.communicate())[0].decode()
        log.debug(f"Server responded to RCON command \"{command}\" with \"{data.strip()}\"")
        return data


rcon_command = Base.rcon_command

__all__ = [
    "rcon_command"
]
