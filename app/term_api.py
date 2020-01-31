from collections import defaultdict
from datetime import datetime
from shutil import which

from aiohttp import web
from aiohttp_jinja2 import template

from app.utility.base_service import BaseService


class TermApi(BaseService):

    def __init__(self, services, socket_conn):
        self.log = self.add_service('term_api', self)
        self.auth_svc = services.get('auth_svc')
        self.file_svc = services.get('file_svc')
        self.contact_svc = services.get('contact_svc')
        self.app_svc = services.get('app_svc')
        self.socket_conn = socket_conn
        self.reverse_report = defaultdict(list)

    @template('terminal.html')
    async def splash(self, request):
        await self.auth_svc.check_permissions(request)
        await self.socket_conn.tcp_handler.refresh()
        return dict(sessions=[dict(id=s.id, info=s.paw) for s in self.socket_conn.tcp_handler.sessions])

    async def download_report(self, request):
        await self.auth_svc.check_permissions(request)
        return web.json_response(dict(self.reverse_report))

    async def dynamically_compile(self, headers):
        name, platform = headers.get('file'), headers.get('platform')
        if which('go') is not None:
            plugin, file_path = await self.file_svc.find_file_path(name)
            ldflags = ['-s', '-w', '-X main.key=%s' % (self.generate_name(size=30),)]
            for param in ['contact', 'socket', 'http']:
                if param in headers:
                    ldflags.append('-X main.%s=%s' % (param, headers[param]))
            output = 'plugins/%s/payloads/%s-%s' % (plugin, name, platform)
            self.log.debug('Dynamically compiling %s' % name)
            await self.file_svc.compile_go(platform, output, file_path, ldflags=' '.join(ldflags))
        return await self.app_svc.retrieve_compiled_file(name, platform)

    async def socket_handler(self, socket, path):
        try:
            session_id = path.split('/')[1]
            cmd = await socket.recv()
            paw = next(i.paw for i in self.socket_conn.tcp_handler.sessions if i.id == int(session_id))
            self.reverse_report[paw].append(dict(date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), cmd=cmd))
            status, reply = await self.socket_conn.tcp_handler.send(session_id, cmd)
            await socket.send(reply.strip())
        except Exception:
            await socket.send('CONNECTION LOST!')
