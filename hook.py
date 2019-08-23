import asyncio
import logging
import random

from pyfiglet import Figlet
from plugins.terminal.app.terminal.shell import Shell
from plugins.terminal.app.utility.console import Console

name = 'Terminal'
description = 'A toolset which supports terminal access'
address = None


async def initialize(app, services):
    data_svc = services.get('data_svc')
    await data_svc.load_data(directory='plugins/terminal/data')
    logging.getLogger().setLevel(logging.FATAL)
    loop = asyncio.get_event_loop()
    show_welcome_msg()
    terminal = start_terminal(loop, services)
    start_socket_listener(loop, terminal)
    Console().hint('Enter "help" at any point')


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
        print('...Reverse-shell listener opened on port %s' % sock)
        h = asyncio.start_server(terminal.session.accept, '0.0.0.0', sock, loop=loop)
        loop.create_task(h)
