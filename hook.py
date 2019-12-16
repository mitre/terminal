import asyncio
import logging

import yaml
import websockets

from plugins.terminal.app.term_svc import TermService

name = 'Terminal'
description = 'A toolset which supports terminal access'
address = '/plugin/terminal/gui'


async def enable(services):
    app = services.get('app_svc').application
    with open('plugins/terminal/conf/terminal_conf.yml', 'r') as fle:
        terminal_config = yaml.safe_load(fle)
    terminal_keys = terminal_config.get('terminal_keys')
    term_svc = TermService(services, terminal_keys)
    await term_svc.start_socket_listener()
    app.router.add_route('GET', '/plugin/terminal/gui', term_svc.splash)
    app.router.add_static('/terminal', 'plugins/terminal/static/', append_version=True)

    await services.get('file_svc').add_special_payload('reverse.go', term_svc.dynamically_compile)
    await services.get('data_svc').load_data(directory='plugins/terminal/data')

    logging.getLogger('websockets').setLevel(logging.FATAL)
    asyncio.get_event_loop().create_task(start_server(term_svc))


async def start_server(term_svc):
    await websockets.serve(term_svc.socket_handler, 'localhost', 8765)
