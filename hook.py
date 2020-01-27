import asyncio
import logging
import websockets

from plugins.terminal.app.contact_tcp import Tcp
from plugins.terminal.app.term_api import TermApi

name = 'Terminal'
description = 'A toolset which supports terminal access'
address = '/plugin/terminal/gui'


async def enable(services):
    await services.get('data_svc').apply('sessions')
    app = services.get('app_svc').application
    tcp_conn = Tcp(services)
    term_api = TermApi(services, tcp_conn)
    app.router.add_static('/terminal', 'plugins/terminal/static/', append_version=True)
    app.router.add_route('GET', '/plugin/terminal/gui', term_api.splash)

    await services.get('contact_svc').register(tcp_conn)
    await services.get('file_svc').add_special_payload('reverse.go', term_api.dynamically_compile)
    await services.get('data_svc').load_data(directory='plugins/terminal/data')

    logging.getLogger('websockets').setLevel(logging.FATAL)
    asyncio.get_event_loop().create_task(start_emulator_connection(term_api))


async def start_emulator_connection(term_api):
    await websockets.serve(term_api.socket_handler, 'localhost', 8765)
