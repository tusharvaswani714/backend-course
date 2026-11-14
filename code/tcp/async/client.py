import asyncio

HOST = "127.0.0.1"
PORT = 9000


class ChatClient:
    async def receive(self, reader):
        while True:
            line = await reader.readline()
            if not line:
                print("\nserver closed the connection")
                return
            print(f"\nserver: {line.decode().rstrip()}")

    async def send(self, writer):
        while True:
            # input() blocks, so it runs in a thread. The event loop keeps receiving messages meanwhile.
            message = await asyncio.to_thread(input, "you: ")
            writer.write(f"{message}\n".encode())
            await writer.drain()

    async def run(self):
        reader, writer = await asyncio.open_connection(HOST, PORT)
        print(f"connected to {HOST}:{PORT}")
        tasks = [asyncio.create_task(self.receive(reader)), asyncio.create_task(self.send(writer))]
        await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for task in tasks:
            task.cancel()
        writer.close()


if __name__ == "__main__":
    asyncio.run(ChatClient().run())
