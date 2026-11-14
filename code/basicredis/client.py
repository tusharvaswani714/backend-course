import json
import shlex
import socket

HOST = "127.0.0.1"
PORT = 6380


def frame(payload):
    body = json.dumps(payload).replace("<", "\\u003c").replace(">", "\\u003e")
    return f"<<{body}>>\n".encode()


def read_reply(reader):
    line = reader.readline()
    if not line:
        return None
    return json.loads(line.strip()[2:-2])


def show(reply):
    if reply is None:
        print("server closed the connection")
        return
    kind = reply["type"]
    if kind == "error":
        print(f"(error) {reply['value']}")
    elif kind == "integer":
        print(f"(integer) {reply['value']}")
    elif kind == "nil":
        print("(nil)")
    elif kind == "list":
        for index, item in enumerate(reply["value"], 1):
            print(f"{index}) {item}")
    else:
        print(reply["value"])


def main():
    with socket.create_connection((HOST, PORT)) as sock:
        reader = sock.makefile("rb")
        print(f"connected to {HOST}:{PORT}")
        try:
            while True:
                line = input(f"{HOST}:{PORT}> ").strip()
                if not line:
                    continue
                args = shlex.split(line)
                if args[0].lower() == "quit":
                    break
                sock.sendall(frame(args))
                show(read_reply(reader))
        except (KeyboardInterrupt, EOFError):
            pass
        finally:
            reader.close()


if __name__ == "__main__":
    main()
