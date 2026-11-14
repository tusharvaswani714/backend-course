import fnmatch
import json
import socket
import threading

HOST = "127.0.0.1"
PORT = 6380

store = {}
lock = threading.Lock()


def frame(payload):
    body = json.dumps(payload).replace("<", "\\u003c").replace(">", "\\u003e")
    return f"<<{body}>>\n".encode()


def parse_command(line):
    line = line.strip()
    if not (line.startswith(b"<<") and line.endswith(b">>")):
        raise ValueError("bad frame")
    args = json.loads(line[2:-2])
    if not isinstance(args, list) or not args:
        raise ValueError("bad command")
    return args


def simple(text):
    return {"type": "string", "value": text}


def error(text):
    return {"type": "error", "value": text}


def integer(value):
    return {"type": "integer", "value": value}


def bulk(value):
    if value is None:
        return {"type": "nil"}
    return {"type": "bulk", "value": str(value)}


def array(items):
    return {"type": "list", "value": [str(item) for item in items]}


def run(args):
    name = args[0].upper()
    params = args[1:]

    if name == "PING":
        return bulk(params[0]) if params else simple("PONG")

    if name == "GET":
        return bulk(store.get(params[0]))

    if name == "EXISTS":
        return integer(sum(1 for key in params if key in store))

    with lock:
        if name == "SET":
            store[params[0]] = params[1]
            return simple("OK")

        if name == "DEL":
            removed = 0
            for key in params:
                if store.pop(key, None) is not None:
                    removed += 1
            return integer(removed)

        if name == "INCR":
            key = params[0]
            try:
                value = int(store.get(key, "0")) + 1
            except ValueError:
                return error("value is not an integer or out of range")
            store[key] = str(value)
            return integer(value)

        if name == "KEYS":
            return array([key for key in store if fnmatch.fnmatch(key, params[0])])

    return error(f"unknown command '{name}'")


def execute(args):
    try:
        return run(args)
    except IndexError:
        return error(f"wrong number of arguments for '{args[0].lower()}'")


def handle(conn, addr):
    pending = b""
    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            pending += data
            while b"\n" in pending:
                line, pending = pending.split(b"\n", 1)
                try:
                    args = parse_command(line)
                except ValueError:
                    conn.sendall(frame(error("protocol error")))
                    return
                conn.sendall(frame(execute(args)))
    except OSError:
        pass
    finally:
        conn.close()
        print(f"disconnected: {addr}")


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        print(f"basic redis listening on {HOST}:{PORT}")

        try:
            while True:
                conn, addr = server.accept()
                print(f"connected: {addr}")
                threading.Thread(target=handle, args=(conn, addr), daemon=True).start()
        except KeyboardInterrupt:
            print("\nshutting down")


if __name__ == "__main__":
    main()
