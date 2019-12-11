import socket

from plugins.terminal.app.utility.console import Console


class Session:

    def __init__(self, services):
        self.services = services
        self.sessions = []
        self.term_svc = services.get('term_svc')
        self.console = Console()
        self.seen_ips = set()

    async def accept(self, reader, writer):
        if not (await self._handshake(reader, writer)):
            return
        connection = writer.get_extra_info('socket')
        shell_info = await self._get_shell_info(reader)
        self.sessions.append(dict(id=len(self.sessions) + 1, paw=shell_info, connection=connection))
        self.console.line('New session: %s' % shell_info)

    async def refresh(self):
        for index, session in enumerate(self.sessions):
            try:
                session.get('connection').send(str.encode(' '))
            except socket.error:
                del self.sessions[index]

    async def has_agent(self, paw):
        agents = await self.services.get('data_svc').locate('agents')
        return next((i for i in agents if i['paw'] == paw), False)

    async def _handshake(self, reader, writer):
        recv_proof = (await reader.readline()).strip()
        remote_socket = writer.get_extra_info('socket').getpeername()
        if recv_proof.decode() in self.term_svc.terminal_keys:
            return True
        elif remote_socket[0] in self.seen_ips:  # already seen, don't re-notify that this is blocked
            writer.close()
            return False
        else:
            self.console.line(
                'Blocked an incoming connection from {} with incorrect terminal_key value {}\n'.format(remote_socket,
                                                                                                       recv_proof))
            self.seen_ips.add(remote_socket[0])
            writer.close()
            return False

    async def _get_shell_info(self, reader):
        x = (await reader.readline()).strip().decode()
        return x
