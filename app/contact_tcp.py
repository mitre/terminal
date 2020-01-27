import asyncio
import json
import socket
import time

from app.utility.base_world import BaseWorld
from plugins.terminal.app.c_session import Session


class Tcp(BaseWorld):

    def __init__(self, services):
        self.name = 'tcp'
        self.log = self.create_logger('basic_tcp')
        self.contact_svc = services.get('contact_svc')
        self.tcp_ports = services.get('app_svc').config['secrets']['terminal']['tcp_ports']
        terminal_keys = services.get('app_svc').config['secrets']['terminal']['terminal_keys']
        self.handler = SessionHandler(services, terminal_keys)

    def start(self):
        loop = asyncio.get_event_loop()
        for sock in self.tcp_ports:
            h = asyncio.start_server(self.handler.accept, '0.0.0.0', sock, loop=loop)
            loop.create_task(h)
            loop.create_task(self.operation_loop())

    async def operation_loop(self):
        try:
            while True:
                for session in self.handler.sessions:
                    instructions = json.loads(await self.contact_svc.get_instructions(session.paw))
                    for i in instructions:
                        instruction = json.loads(i)
                        self.log.debug('TCP instruction: %s' % instruction['id'])
                        _, status, response = await self.handler.send(session.id, self.decode_bytes(instruction['command']))
                        await self.contact_svc.save_results(id=instruction['id'], output=self.encode_string(response), status=status, pid=0)
                        await asyncio.sleep(instruction['sleep'])
                await asyncio.sleep(20)
        except Exception as e:
            self.log.debug('operation error: %s' % e)

    @staticmethod
    def valid_config():
        return True


class ShellHandshakeFailure(ConnectionError):
    pass


class SessionHandler(BaseWorld):

    def __init__(self, services, terminal_keys):
        self.services = services
        self.terminal_keys = terminal_keys
        self.sessions = []
        self.seen_ips = set()

    async def refresh(self):
        for index, session in enumerate(self.sessions):
            try:
                session.connection.send(str.encode(' '))
            except socket.error:
                del self.sessions[index]

    async def accept(self, reader, writer):
        try:
            profile = await self._handshake(reader, writer)
        except ShellHandshakeFailure:
            return
        connection = writer.get_extra_info('socket')
        parts = profile.split('$')
        structured_profile = dict(
            host=parts[0], username=parts[1], platform=parts[2], architecture=parts[3], executors=parts[4].split(','),
            contact='tcp'
        )
        agent = await self.services.get('contact_svc').handle_heartbeat(**structured_profile)
        new_session = Session(id=len(self.sessions) + 1, paw=agent.paw, connection=connection)
        self.sessions.append(new_session)
        await self.send(new_session.id, agent.paw)

    async def send(self, session_id, cmd):
        conn = next(i.connection for i in self.sessions if i.id == int(session_id))
        conn.send(str.encode(' '))
        conn.send(str.encode('%s\n' % cmd))
        raw_response = await self._attempt_connection(conn, 100)
        return raw_response.split('$')[0], raw_response.split('$')[1], raw_response.split('$')[2]

    """ PRIVATE """

    async def _handshake(self, reader, writer):
        recv_proof = (await reader.readline()).strip()
        remote_socket = writer.get_extra_info('socket').getpeername()
        if recv_proof.decode() in self.terminal_keys:
            return (await reader.readline()).strip().decode()
        elif remote_socket[0] in self.seen_ips:
            writer.close()
            raise ShellHandshakeFailure
        else:
            self.seen_ips.add(remote_socket[0])
            writer.close()
            raise ShellHandshakeFailure

    @staticmethod
    async def _attempt_connection(connection, max_tries):
        attempts = 0
        client_response = None
        while not client_response:
            try:
                client_response = str(connection.recv(4096), 'utf-8')
            except BlockingIOError as err:
                if attempts > max_tries:
                    raise err
                attempts += 1
                time.sleep(.1 * attempts)
        return client_response
