import asyncio

HOST = "127.0.0.1"
PORT = 9001


class ChatClient(asyncio.DatagramProtocol):
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        print(f"\nserver: {data.decode()}")

    async def console(self):
        while True:
            # input() blocks, so it runs in a thread. The event loop keeps receiving datagrams meanwhile.
            message = await asyncio.to_thread(input, "you: ")
            self.transport.sendto(message.encode())

    async def run(self):
        loop = asyncio.get_running_loop()
        transport, _ = await loop.create_datagram_endpoint(lambda: self, remote_addr=(HOST, PORT))
        transport.sendto(b"/join")
        print(f"sending to {HOST}:{PORT}")
        try:
            await self.console()
        except (KeyboardInterrupt, EOFError):
            pass
        finally:
            transport.close()


if __name__ == "__main__":
    asyncio.run(ChatClient().run())
