import asyncio
import random
import string
from shutil import which

from aiohttp_jinja2 import template

from app.utility.base_service import BaseService
from plugins.terminal.app.session import SessionHandler


class TermService(BaseService):

    def __init__(self, services, terminal_keys):
        self.log = self.add_service('term_svc', self)
        self.services = services
        self.handler = SessionHandler(terminal_keys)

    @template('terminal.html')
    async def splash(self, request):
        await self.services.get('auth_svc').check_permissions(request)
        await self.handler.refresh()
        return dict(sessions=[dict(id=s['id'], info=s['shell_info']) for s in self.handler.sessions])

    async def start_socket_listener(self):
        loop = asyncio.get_event_loop()
        for sock in [5678]:
            h = asyncio.start_server(self.handler.accept, '0.0.0.0', sock, loop=loop)
            loop.create_task(h)

    async def dynamically_compile(self, headers):
        name, platform = headers.get('file'), headers.get('platform')
        if which('go') is not None:
            plugin, file_path = await self.services.get('file_svc').find_file_path(name)

            ldflags = ['-s', '-w', '-X main.key=%s' % self._generate_key()]

            output = 'plugins/%s/payloads/%s-%s' % (plugin, name, platform)
            self.log.debug('Dynamically compiling %s' % name)
            await self.services.get('file_svc').compile_go(platform, output, file_path, ldflags=' '.join(ldflags))
        return '%s-%s' % (name, platform), self.generate_name(10)

    async def socket_handler(self, socket, path):
        try:
            session_id = path.split('/')[1]
            cmd = await socket.recv()
            reply = await self.handler.send(session_id, cmd)
            await socket.send(reply.strip())
        except Exception:
            await socket.send('CONNECTION LOST!')

    """ PRIVATE """

    @staticmethod
    def _generate_key(size=30):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(size))
