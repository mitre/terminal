import asyncio
import glob
import random

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
                    'agents': lambda _: self._show_agents(),
                    'pick': lambda c: self._start_agent_shell(cmd)
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
        print('-> agents: show all')
        print('-> pick [n]: pick an agent by ID to interact with')
        print('-> logs [n]: view the last n-lines of each log file')

    @staticmethod
    async def _print_logs(cmd):
        n = int(cmd.split(' ')[1])
        for name in glob.iglob('logs/*.log', recursive=False):
            with open(name, 'r') as f:
                print('***** %s ***** ' % name)
                lines = f.readlines()
                print(*lines[-n:])

    async def _start_agent_shell(self, cmd):
        await self.agent_shell.enter(cmd.split(' ')[1])

    async def _show_agents(self):
        agents = [dict(id=a['id'], paw=a['paw'], agent=True,
                       session=next((True for i in self.session.sessions if i['paw'] == a['paw']), False))
                  for a in await self.data_svc.dao.get('core_agent')]
        for s in self.session.sessions:
            if not next((i for i in agents if i['paw'] == s['paw']), False):
                agents.append(dict(id=random.randint(1000, 2000), paw=s['paw'], agent=False, session=True))
        await self.console.table(agents)
