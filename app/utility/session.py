import socket

from plugins.terminal.app.utility.console import Console


class Session:

    def __init__(self, services, log):
        self.log = log
        self.services = services
        self.sessions = []
        self.console = Console()

    async def accept(self, reader, writer):
        connection = writer.get_extra_info('socket')
        paw = await self._gen_paw_print(connection)
        self.sessions.append(dict(id=len(self.sessions) + 1, paw=paw, connection=connection))
        self.console.line('New session: %s' % paw)

    async def refresh(self):
        for index, session in enumerate(self.sessions):
            try:
                session.get('connection').send(str.encode(' '))
            except socket.error:
                del self.sessions[index]

    async def has_agent(self, paw):
        agents = await self.services.get('data_svc').explode('agent')
        return next((i for i in agents if i['paw'] == paw), False)

    @staticmethod
    async def _gen_paw_print(connection):
        paw = ''
        while True:
            try:
                data = str(connection.recv(1), 'utf-8')
                paw += data
            except BlockingIOError:
                break
        return paw
