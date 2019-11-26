import asyncio

from plugins.terminal.app.terminal.shell import Shell


class TCPSocket:

    def __init__(self, services):
        self.services = services
        self.port = 5678

    async def start(self):
        loop = asyncio.get_event_loop()
        terminal = await self._start_terminal(loop)
        await self._start_socket_listener(loop, terminal)

    """ PRIVATE """

    async def _start_terminal(self, loop):
        terminal = Shell(self.services)
        loop.create_task(terminal.start())
        return terminal

    async def _start_socket_listener(self, loop, terminal):
        for sock in [self.port]:
            h = asyncio.start_server(terminal.session.accept, '0.0.0.0', sock, loop=loop)
            loop.create_task(h)
