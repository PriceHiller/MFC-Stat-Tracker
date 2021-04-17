import asyncio

from srcds.rcon import RconConnection


def main():
    conn = RconConnection("45.76.25.27", port=26003, password="NGI3MmVkN2FiZTQzYzFiMWQ3NWNlYjA2", single_packet_mode=True)
    command = conn.exec_command("listen allon")


    while True:
        response = conn.read_response()
        aids = bytes(response.body[:-3]) # chode code
        string = aids.decode("ascii", errors = "ignore").encode("ascii", errors = "ignore")
        normalization = string.decode(encoding = "UTF-8").strip().replace("  ", " ").replace("\t", " ")

        partials = normalization.split(":")
        print("".join("\n - " + partial for partial in partials))

if __name__ == "__main__":
    main()