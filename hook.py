from app.utility.base_world import BaseWorld
from plugins.terminal.app.h_terminal import Handle
from plugins.terminal.app.term_api import TermApi

name = 'Terminal'
description = 'A toolset which supports terminal access'
address = '/plugin/terminal/gui'
access = BaseWorld.Access.RED


async def enable(services):
    await services.get('data_svc').apply('sessions')
    app = services.get('app_svc').application
    term_api = TermApi(services)

    udp_contact = [c for c in services.get('contact_svc').contacts if c.name == 'websocket']
    udp_contact[0].handler.handles.append(Handle(tag='terminal'))

    app.router.add_static('/terminal', 'plugins/terminal/static/', append_version=True)
    app.router.add_route('GET', '/plugin/terminal/gui', term_api.splash)
    app.router.add_route('POST', '/plugin/terminal/sessions', term_api.sessions)
    app.router.add_route('POST', '/plugin/terminal/history', term_api.get_history)
    app.router.add_route('POST', '/plugin/terminal/ability', term_api.get_abilities)
    await services.get('file_svc').add_special_payload('manx.go', term_api.dynamically_compile)
