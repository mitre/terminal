import asyncio
import random
import string

from shutil import which

from aiohttp_jinja2 import template

from plugins.terminal.app.terminal.zero import Zero
from plugins.terminal.app.utility.session import Session


class TermService:

    def __init__(self, services, terminal_keys):
        self.file_svc = services.get('file_svc')
        self.auth_svc = services.get('auth_svc')
        self.terminal_keys = terminal_keys
        self.services = services
        self.session = None

    @template('terminal.html')
    async def splash(self, request):
        await self.auth_svc.check_permissions(request)
        return dict(sessions=[dict(id=s['id'], connection=s['connection']) for s in self.session.sessions])

    async def pop_box(self, request):
        await self.auth_svc.check_permissions(request)
        data = dict(await request.json())
        await asyncio.create_task(self._connect_session(data['id']))

    async def dynamically_compile(self, headers):
        name, platform = headers.get('file'), headers.get('platform')
        if which('go') is not None:
            plugin, file_path = await self.file_svc.find_file_path(name)
            ldflags = ['-s', '-w', '-X main.key=%s' % self._generate_key()]

            output = 'plugins/%s/payloads/%s-%s' % (plugin, name, platform)
            self.file_svc.log.debug('Dynamically compiling %s' % name)
            await self.file_svc.compile_go(platform, output, file_path, ldflags=' '.join(ldflags))
        return '%s-%s' % (name, platform), '%s-%s' % (name, platform)

    async def set_session(self):
        self.session = Session(self.services)

    async def start_socket_listener(self):
        loop = asyncio.get_event_loop()
        for sock in [5678]:
            h = asyncio.start_server(self.session.accept, '0.0.0.0', sock, loop=loop)
            loop.create_task(h)

    """ PRIVATE """

    @staticmethod
    def _generate_key(size=30):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(size))

    async def _connect_session(self, identifier):
        try:
            conn = next(i['connection'] for i in self.session.sessions if i['id'] == int(identifier))
            conn.setblocking(True)
            conn.send(str.encode(' '))
            await Zero(conn).enter()
        except StopIteration:
            pass
