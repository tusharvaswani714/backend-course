import asyncio

HOST = "127.0.0.1"
PORT = 9000


class ChatServer:
    def __init__(self):
        self.clients = {}
        self.next_id = 1

    async def receive(self, client_id, reader):
        while True:
            line = await reader.readline()
            if not line:
                return
            print(f"\n[{client_id}] client: {line.decode().rstrip()}")

    async def handle(self, reader, writer):
        client_id = self.next_id
        self.next_id += 1
        self.clients[client_id] = writer
        print(f"\nclient {client_id} connected from {writer.get_extra_info('peername')}")
        try:
            await self.receive(client_id, reader)
        except ConnectionError:
            pass
        finally:
            self.clients.pop(client_id, None)
            writer.close()
            print(f"\nclient {client_id} left")

    async def send_private(self, client_id, text):
        writer = self.clients.get(client_id)
        if writer is None:
            print(f"no client with id {client_id}")
            return
        try:
            writer.write(f"{text}\n".encode())
            await writer.drain()
        except ConnectionError:
            print(f"could not reach client {client_id}")

    async def handle_command(self, line):
        if line == "/clients":
            print("connected clients:", list(self.clients) or "none")
            return
        parts = line.split(" ", 2)
        if len(parts) == 3 and parts[0] == "/to" and parts[1].isdigit():
            await self.send_private(int(parts[1]), parts[2])
            return
        print("usage: /to <id> <message>  or  /clients")

    async def console(self):
        while True:
            # input() blocks, so it runs in a thread. The event loop keeps serving clients meanwhile.
            line = (await asyncio.to_thread(input, "you: ")).strip()
            if line:
                await self.handle_command(line)

    async def run(self):
        server = await asyncio.start_server(self.handle, HOST, PORT)
        print(f"waiting for clients on {HOST}:{PORT}")
        async with server:
            try:
                await self.console()
            except (KeyboardInterrupt, EOFError):
                pass


if __name__ == "__main__":
    asyncio.run(ChatServer().run())
