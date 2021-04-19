import asyncio

from tracker import Base


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Base.run())


if __name__ == "__main__":
    main()
