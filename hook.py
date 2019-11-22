import logging
import random

import yaml
from pyfiglet import Figlet

from plugins.terminal.app.utility.console import Console
from plugins.terminal.app.term_svc import TermService

name = 'Terminal'
description = 'A toolset which supports terminal access'
address = None


async def enable(app, services):
    with open('plugins/terminal/conf/terminal_conf.yml', 'r') as fle:
        terminal_config = yaml.safe_load(fle)
    terminal_keys = terminal_config.get('terminal_keys')
    file_svc = services.get('file_svc')
    term_svc = TermService(file_svc, terminal_keys)
    services['term_svc'] = term_svc
    await file_svc.add_special_payload('reverse.go', term_svc.dynamically_compile)
    data_svc = services.get('data_svc')
    await data_svc.load_data(directory='plugins/terminal/data')
    logging.getLogger().setLevel(logging.FATAL)
    show_welcome_msg()
    Console().hint('Enter "help" at any point')


def show_welcome_msg():
    custom_fig = Figlet(font='contrast')
    new_font = random.choice(custom_fig.getFonts())
    custom_fig.setFont(font=new_font)
    print(custom_fig.renderText('caldera'))
