import socket
import threading

HOST = "127.0.0.1"
PORT = 9000


class ChatServer:
    def __init__(self):
        self.clients = {}
        self.next_id = 1

    def receive(self, client_id, reader):
        try:
            for line in reader:
                print(f"\n[{client_id}] client: {line.decode().rstrip()}")
        except (OSError, ValueError):
            pass
        finally:
            self.clients.pop(client_id, None)
            print(f"\nclient {client_id} left")

    def accept_clients(self, server):
        try:
            while True:
                conn, addr = server.accept()
                client_id = self.next_id
                self.next_id += 1
                self.clients[client_id] = conn
                print(f"\nclient {client_id} connected from {addr}")
                threading.Thread(target=self.receive, args=(client_id, conn.makefile("rb")), daemon=True).start()
        except OSError:
            pass

    def send_private(self, client_id, text):
        conn = self.clients.get(client_id)
        if conn is None:
            print(f"no client with id {client_id}")
            return
        try:
            conn.sendall(f"{text}\n".encode())
        except OSError:
            print(f"could not reach client {client_id}")

    def handle_command(self, line):
        if line == "/clients":
            print("connected clients:", list(self.clients) or "none")
            return
        parts = line.split(" ", 2)
        if len(parts) == 3 and parts[0] == "/to" and parts[1].isdigit():
            self.send_private(int(parts[1]), parts[2])
            return
        print("usage: /to <id> <message>  or  /clients")

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((HOST, PORT))
            server.listen()
            print(f"waiting for clients on {HOST}:{PORT}")
            threading.Thread(target=self.accept_clients, args=(server,), daemon=True).start()

            try:
                while True:
                    line = input("you: ").strip()
                    if line:
                        self.handle_command(line)
            except (KeyboardInterrupt, EOFError):
                pass
            finally:
                for conn in self.clients.values():
                    conn.close()


if __name__ == "__main__":
    ChatServer().run()
