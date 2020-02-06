import asyncio
import json
import logging

import websockets

from plugins.terminal.app.contact_tcp import Tcp
from plugins.terminal.app.contact_udp import Udp
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
    app.router.add_route('POST', '/plugin/terminal/report', term_api.download_report)

    await services.get('contact_svc').register(tcp_conn)
    await services.get('contact_svc').register(Udp(services))
    await services.get('file_svc').add_special_payload('manx.go', term_api.dynamically_compile)

    logging.getLogger('websockets').setLevel(logging.FATAL)
    asyncio.get_event_loop().create_task(start_emulator_connection(term_api))


async def destroy(services):
    r_dir = await services['file_svc'].create_exfil_sub_directory(
        '%s/reports' % services['app_svc'].config['reports_dir']
    )
    report = json.dumps(dict(services['term_api'].reverse_report)).encode()
    await services['file_svc'].save_file('reverse_report', report, r_dir)


async def start_emulator_connection(term_api):
    await websockets.serve(term_api.socket_handler, 'localhost', 8765)
