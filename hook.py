import asyncio
import logging
import random

from pyfiglet import Figlet
from plugins.offensive.app.terminal.shell import Shell

name = 'Offensive'
description = 'A toolset which turns CALDERA into an offensive package'
address = None


async def initialize(app, services):
    data_svc = services.get('data_svc')
    await data_svc.reload_database(abilities='plugins/offensive/abilities')

    logging.getLogger().setLevel(logging.FATAL)
    loop = asyncio.get_event_loop()
    show_welcome_msg()
    terminal = start_terminal(loop, services)
    start_socket_listener(loop, terminal)


def show_welcome_msg():
    custom_fig = Figlet(font='contrast')
    new_font = random.choice(custom_fig.getFonts())
    custom_fig.setFont(font=new_font)
    print(custom_fig.renderText('caldera'))


def start_terminal(loop, services):
    terminal = Shell(services)
    loop.create_task(terminal.start())
    return terminal


def start_socket_listener(loop, terminal):
    for sock in [5678]:
        print('...Socket opened on port %s' % sock)
        h = asyncio.start_server(terminal.session.accept, '0.0.0.0', sock, loop=loop)
        loop.create_task(h)
