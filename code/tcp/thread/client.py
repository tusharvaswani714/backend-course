import socket
import threading

HOST = "127.0.0.1"
PORT = 9000


class ChatClient:
    def receive(self, sock):
        try:
            for line in sock.makefile("rb"):
                print(f"\nserver: {line.decode().rstrip()}")
        except OSError:
            pass

    def run(self):
        with socket.create_connection((HOST, PORT)) as sock:
            print(f"connected to {HOST}:{PORT}")
            threading.Thread(target=self.receive, args=(sock,), daemon=True).start()

            try:
                while True:
                    message = input("you: ")
                    sock.sendall(f"{message}\n".encode())
            except (KeyboardInterrupt, EOFError, BrokenPipeError):
                pass


if __name__ == "__main__":
    ChatClient().run()
