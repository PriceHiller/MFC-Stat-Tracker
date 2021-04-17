from srcds.rcon import RconConnection

from tracker.events import EventListener


class Base:
    connection = RconConnection("45.76.25.27", port=26003, password="NGI3MmVkN2FiZTQzYzFiMWQ3NWNlYjA2",
                                single_packet_mode=True)

    @classmethod
    def run(cls):
        command = cls.connection.exec_command("listen allon")

    @classmethod
    def parse_event(cls, event_name: str, event_content: str):

print(EventListener.events)
