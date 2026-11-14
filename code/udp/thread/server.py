import socket
import threading

HOST = "127.0.0.1"
PORT = 9001


class ChatServer:
    def __init__(self):
        self.clients = {}
        self.client_ids = {}
        self.next_id = 1

    def register(self, addr):
        if addr not in self.client_ids:
            client_id = self.next_id
            self.next_id += 1
            self.clients[client_id] = addr
            self.client_ids[addr] = client_id
            print(f"\nclient {client_id} joined from {addr}")
        return self.client_ids[addr]

    def receive(self, sock):
        try:
            while True:
                data, addr = sock.recvfrom(1024)
                client_id = self.register(addr)
                if data != b"/join":
                    print(f"\n[{client_id}] client: {data.decode()}")
        except OSError:
            pass

    def send_private(self, sock, client_id, text):
        addr = self.clients.get(client_id)
        if addr is None:
            print(f"no client with id {client_id}")
            return
        sock.sendto(text.encode(), addr)

    def handle_command(self, sock, line):
        if line == "/clients":
            print("connected clients:", list(self.clients) or "none")
            return
        parts = line.split(" ", 2)
        if len(parts) == 3 and parts[0] == "/to" and parts[1].isdigit():
            self.send_private(sock, int(parts[1]), parts[2])
            return
        print("usage: /to <id> <message>  or  /clients")

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind((HOST, PORT))
            print(f"waiting for clients on {HOST}:{PORT}")
            threading.Thread(target=self.receive, args=(sock,), daemon=True).start()

            try:
                while True:
                    line = input("you: ").strip()
                    if line:
                        self.handle_command(sock, line)
            except (KeyboardInterrupt, EOFError):
                pass


if __name__ == "__main__":
    ChatServer().run()
