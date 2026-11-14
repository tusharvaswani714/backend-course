import asyncio

HOST = "127.0.0.1"
PORT = 9001


class ChatServer(asyncio.DatagramProtocol):
    def __init__(self):
        self.clients = {}
        self.client_ids = {}
        self.next_id = 1

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        client_id = self.register(addr)
        if data != b"/join":
            print(f"\n[{client_id}] client: {data.decode()}")

    def register(self, addr):
        if addr not in self.client_ids:
            client_id = self.next_id
            self.next_id += 1
            self.clients[client_id] = addr
            self.client_ids[addr] = client_id
            print(f"\nclient {client_id} joined from {addr}")
        return self.client_ids[addr]

    def send_private(self, client_id, text):
        addr = self.clients.get(client_id)
        if addr is None:
            print(f"no client with id {client_id}")
            return
        self.transport.sendto(text.encode(), addr)

    def handle_command(self, line):
        if line == "/clients":
            print("connected clients:", list(self.clients) or "none")
            return
        parts = line.split(" ", 2)
        if len(parts) == 3 and parts[0] == "/to" and parts[1].isdigit():
            self.send_private(int(parts[1]), parts[2])
            return
        print("usage: /to <id> <message>  or  /clients")

    async def console(self):
        while True:
            # input() blocks, so it runs in a thread. The event loop keeps receiving datagrams meanwhile.
            line = (await asyncio.to_thread(input, "you: ")).strip()
            if line:
                self.handle_command(line)

    async def run(self):
        loop = asyncio.get_running_loop()
        transport, _ = await loop.create_datagram_endpoint(lambda: self, local_addr=(HOST, PORT))
        print(f"waiting for clients on {HOST}:{PORT}")
        try:
            await self.console()
        except (KeyboardInterrupt, EOFError):
            pass
        finally:
            transport.close()


if __name__ == "__main__":
    asyncio.run(ChatServer().run())
