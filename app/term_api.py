from shutil import which

from aiohttp import web
from aiohttp_jinja2 import template

from app.service.auth_svc import red_authorization
from app.utility.base_service import BaseService
from plugins.terminal.app.term_svc import TermService


class TermApi(BaseService):

    def __init__(self, services):
        self.auth_svc = services.get('auth_svc')
        self.file_svc = services.get('file_svc')
        self.data_svc = services.get('data_svc')
        self.contact_svc = services.get('contact_svc')
        self.app_svc = services.get('app_svc')
        self.rest_svc = services.get('rest_svc')
        self.term_svc = TermService(services)

    @red_authorization
    @template('terminal.html')
    async def splash(self, request):
        await self.term_svc.socket_conn.tcp_handler.refresh()
        sessions = [dict(id=s.id, info=s.paw) for s in self.term_svc.socket_conn.tcp_handler.sessions]
        delivery_cmds = [
            c.display for c in await self.data_svc.locate('abilities', dict(ability_id='356d1722-7784-40c4-822b-0cf864b0b36d'))
        ]
        return dict(sessions=sessions, delivery_cmds=delivery_cmds, websocket=self.get_config('app.contact.websocket'))

    @red_authorization
    async def sessions(self, request):
        await self.term_svc.socket_conn.tcp_handler.refresh()
        sessions = [dict(id=s.id, info=s.paw) for s in self.term_svc.socket_conn.tcp_handler.sessions]
        return web.json_response(sessions)

    @red_authorization
    async def download_report(self, request):
        data = dict(await request.json())
        if data.get('id'):
            return web.json_response(self.term_svc.reverse_report[data['id']])
        return web.json_response(dict(self.term_svc.reverse_report))

    @red_authorization
    async def get_abilities(self, request):
        data = dict(await request.json())
        abilities = await self.rest_svc.find_abilities(paw=data['paw'])
        return web.json_response(dict(abilities=[a.display for a in abilities]))

    async def dynamically_compile(self, headers):
        name, platform = headers.get('file'), headers.get('platform')
        if which('go') is not None:
            plugin, file_path = await self.file_svc.find_file_path(name)
            ldflags = ['-s', '-w', '-X main.key=%s' % (self.generate_name(size=30),)]
            for param in ['contact', 'socket', 'http']:
                if param in headers:
                    ldflags.append('-X main.%s=%s' % (param, headers[param]))
            output = 'plugins/%s/payloads/%s-%s' % (plugin, name, platform)
            await self.file_svc.compile_go(platform, output, file_path, ldflags=' '.join(ldflags))
        return await self.app_svc.retrieve_compiled_file(name, platform)
