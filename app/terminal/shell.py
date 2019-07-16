import asyncio
import glob

from aioconsole import ainput

from plugins.offensive.app.terminal.agent import Agent
from plugins.offensive.app.utility.console import Console
from plugins.offensive.app.utility.session import Session


class Shell:

    def __init__(self, services):
        self.data_svc = services.get('data_svc')
        self.log = services.get('utility_svc').create_logger('terminal')
        self.session = Session(services, self.log)
        self.agent_shell = Agent(services, self.log, self.session)
        self.prompt = 'caldera> '
        self.console = Console()

    async def start(self):
        await asyncio.sleep(1)
        while True:
            try:
                cmd = await ainput(self.prompt)
                self.log.debug(cmd)
                await self.session.refresh()

                commands = {
                    '?': lambda _: self._help(),
                    'logs': lambda c: self._print_logs(c),
                    'p': lambda c: self._start_agent_shell(cmd),
                    'agents': lambda _: self._show_agents(),
                    'abilities': lambda _: self._show_abilities(),
                    ' ': lambda _: self._do_nothing(),
                }
                command = [c for c in commands.keys() if cmd.startswith(c)]
                await commands[command[0]](cmd)
            except IndexError:
                pass
            except Exception as e:
                self.console.line('Error: %s' % e, 'red')

    """ PRIVATE """

    @staticmethod
    async def _help():
        print('HELP MENU:')
        print('-> logs [n]: view the last n-lines of each log file')
        print('-> agents: show all agents')
        print('-> abilities: show all abilities')
        print('-> p [n]: pick an agent to interact with')

    @staticmethod
    async def _print_logs(cmd):
        n = int(cmd.split(' ')[1])
        for name in glob.iglob('logs/*.log', recursive=False):
            with open(name, 'r') as f:
                print('***** %s ***** ' % name)
                lines = f.readlines()
                print(*lines[-n:])

    async def _start_agent_shell(self, cmd):
        a = await self.data_svc.dao.get('core_agent', dict(id=cmd.split(' ')[1]))
        await self.agent_shell.enter(a[0]['paw'])

    async def _show_agents(self):
        agents = await self.data_svc.dao.get('core_agent')
        self.console.table([dict(index=a['id'],
                                 paw=a['paw'],
                                 session=next(('Yes' for a in self.session.sessions if a['paw']), 'No'))
                            for a in agents])

    async def _show_abilities(self):
        abilities = [dict(id=a['id'], name=a['name'], description=a['description'], platform=a['platform'])
                     for a in await self.data_svc.dao.get('core_ability')]
        self.console.table(abilities)

    @staticmethod
    async def _do_nothing():
        pass
