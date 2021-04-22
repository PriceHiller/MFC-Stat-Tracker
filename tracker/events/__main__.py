import asyncio
import enum

from tracker.events import listen
from tracker.events import parse
from tracker.events import Event


class RawStringListeners:

    @staticmethod
    @listen("0")
    async def example_listener_zero(event: Event):
        print(event.content)

    @staticmethod
    @listen("1")
    async def example_listener_one(event: Event):
        print(event.content)

    @staticmethod
    @listen("2")
    async def example_listener_two(event: Event):
        print(event.content)


class EventTypeExample(enum.Enum):
    CONNECT: str = "CONNECTION ESTABLISHED"
    DATA_RECEIVED: str = "DATA"
    CLOSE: str = "CONNECTION CLOSED"


class EventTypeListeners:

    @staticmethod
    @listen(EventTypeExample.CONNECT)
    async def connect(event: Event):
        print(f"Got a connection: {event.content}")

    @staticmethod
    @listen(EventTypeExample.DATA_RECEIVED)
    async def data_received(event: Event):
        print(f"Received data: {event.content}")

    @staticmethod
    @listen(EventTypeExample.CLOSE)
    async def close(event: Event):
        print(f"Closed a connection: {event.content}")


from tracker.events import EventListener


class ExampleSubListener(EventListener):

    def __init__(self):
        super().__init__()


class ExampleSubEvent(Event):
    ...


@listen("SUB EVENT EMISSION")
async def base_sub_handler(event: Event):
    sub_event: ExampleSubEvent = event.content
    await ExampleSubListener().parse_event(sub_event)


@ExampleSubListener().listen("SUB EVENT")
async def example_sub(event: Event):
    print(event.content)


async def main():
    print("Example iteration:")
    print("------------------")
    for i in range(3):
        await parse(Event(str(i), f"Content body: {i}"))

    print("\nExample String Parsing:")
    print("------------------------")
    await parse(Event(str(EventTypeExample.CONNECT), "127.0.0.1:5000"))
    await parse(Event(str(EventTypeExample.DATA_RECEIVED), "welcome to the localhost"))
    await parse(Event(str(EventTypeExample.CLOSE), "127.0.0.1:5000"))

    print("\nExample Sub Event:")
    print("--------------------")
    await parse(
        Event(
            name=str("SUB EVENT EMISSION"),
            content=ExampleSubEvent(name="SUB EVENT", content="Emitted from a sub event!"))
    )


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
