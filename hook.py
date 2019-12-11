import yaml

from plugins.terminal.app.term_svc import TermService

name = 'Terminal'
description = 'A toolset which supports terminal access'
address = '/plugin/terminal/gui'


async def enable(services):
    with open('plugins/terminal/conf/terminal_conf.yml', 'r') as fle:
        terminal_config = yaml.safe_load(fle)
    terminal_keys = terminal_config.get('terminal_keys')
    file_svc = services.get('file_svc')
    term_svc = TermService(services, terminal_keys)
    services['term_svc'] = term_svc
    await term_svc.set_session()
    await term_svc.start_socket_listener()

    await file_svc.add_special_payload('reverse.go', term_svc.dynamically_compile)
    data_svc = services.get('data_svc')
    await data_svc.load_data(directory='plugins/terminal/data')
    services.get('app_svc').application.router.add_route('GET', '/plugin/terminal/gui', term_svc.splash)
    services.get('app_svc').application.router.add_route('PUT', '/plugin/terminal/session', term_svc.pop_box)

