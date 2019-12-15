class SessionHandler:

    def __init__(self, terminal_keys):
        self.terminal_keys = terminal_keys
        self.sessions = []
        self.seen_ips = set()

    async def accept(self, reader, writer):
        if not (await self._handshake(reader, writer)):
            return
        connection = writer.get_extra_info('socket')
        paw = await self._gen_paw_print(connection)
        self.sessions.append(dict(id=len(self.sessions) + 1, paw=paw, connection=connection))

    async def send(self, session_id, cmd):
        conn = next(i['connection'] for i in self.sessions if i['id'] == int(session_id))
        conn.setblocking(True)
        conn.send(str.encode(' '))
        conn.send(str.encode('%s\n' % cmd))
        client_response = str(conn.recv(4096), 'utf-8')
        return client_response

    """ PRIVATE """

    async def _handshake(self, reader, writer):
        recv_proof = (await reader.readline()).strip()
        remote_socket = writer.get_extra_info('socket').getpeername()
        if recv_proof.decode() in self.terminal_keys:
            return True
        elif remote_socket[0] in self.seen_ips:
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
