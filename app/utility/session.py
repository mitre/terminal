import socket


class Session:

    def __init__(self, services):
        self.services = services
        self.sessions = []
        self.term_svc = services.get('term_svc')
        self.seen_ips = set()

    async def accept(self, reader, writer):
        if not (await self._handshake(reader, writer)):
            return
        connection = writer.get_extra_info('socket')
        paw = await self._gen_paw_print(connection)
        self.sessions.append(dict(id=len(self.sessions) + 1, paw=paw, connection=connection))

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
            self.seen_ips.add(remote_socket[0])
            writer.close()
            return False

    @staticmethod
    async def _gen_paw_print(connection):
        paw = ''
        while True:
            try:
                data = str(connection.recv(1), 'utf-8')
                paw += data
            except BlockingIOError:
                pass
            return paw
