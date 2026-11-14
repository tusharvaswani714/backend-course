import socket
import threading

HOST = "127.0.0.1"
PORT = 9001


class ChatClient:
    def receive(self, sock):
        try:
            while True:
                data, _ = sock.recvfrom(1024)
                print(f"\nserver: {data.decode()}")
        except OSError:
            pass

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind((HOST, 0))
            sock.sendto(b"/join", (HOST, PORT))
            print(f"sending to {HOST}:{PORT} from port {sock.getsockname()[1]}")
            threading.Thread(target=self.receive, args=(sock,), daemon=True).start()

            try:
                while True:
                    message = input("you: ")
                    sock.sendto(message.encode(), (HOST, PORT))
            except (KeyboardInterrupt, EOFError):
                pass


if __name__ == "__main__":
    ChatClient().run()
