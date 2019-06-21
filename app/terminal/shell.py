import asyncio
import glob
import re

from aioconsole import ainput

from plugins.offensive.app.terminal.agent import Agent
from plugins.offensive.app.terminal.session import Session
from plugins.offensive.app.utility.console import Console


class Shell:

    def __init__(self, services):
        self.data_svc = services.get('data_svc')
        self.log = services.get('utility_svc').create_logger('terminal')
        self.agent = Agent(services, self.log)
        self.session = Session(services, self.log)
        self.shell_prompt = 'caldera> '
        self.console = Console()

    async def start(self):
        await asyncio.sleep(1)
        while True:
            try:
                cmd = await ainput(self.shell_prompt)
                self.log.debug(cmd)
                match = re.search(r'\((.*?)\)', self.shell_prompt)
                if cmd.startswith('log'):
                    await self._print_logs(int(cmd.split(' ')[1]))
                elif cmd.startswith('agent'):
                    self.console.table(await self.data_svc.dao.get('core_agent'))
                elif cmd.startswith('session'):
                    await self.session.show()
                elif cmd.startswith('pa'):
                    agent_id = cmd.split(' ')[1]
                    self.shell_prompt = 'caldera (agent-%s)> ' % agent_id
                elif cmd.startswith('ps'):
                    session_id = cmd.split(' ')[1]
                    self.shell_prompt = 'caldera (session-%s)> ' % session_id
                elif match and 'agent' in match.group(1):
                    obj, index = tuple(match.group(1).split('-'))
                    a = await self.data_svc.dao.get('core_agent', dict(id=index))
                    await self.agent.enter(a[0]['paw'], cmd)
                elif match and 'session' in match.group(1):
                    obj, index = tuple(match.group(1).split('-'))
                    await self.session.enter(int(index), cmd)
                elif cmd == '?':
                    await self._print_help()
                elif cmd == '':
                    pass
                else:
                    self.console.line('Bad command - are you sure?', 'red')
            except IndexError:
                pass
            except Exception as e:
                self.console.line('Error: %s' % e, 'red')

    @staticmethod
    async def _print_help():
        print('HELP MENU:')
        print('-> agents: show all agents')
        print('-> sessions: show all active sessions')
        print('-> pa [n]: pick an agent to interact with')
        print('-> ps [n]: pick a session to interact with')
        print('-> logs [n]: view the last n-lines of each log file')

    @staticmethod
    async def _print_logs(n):
        for name in glob.iglob('logs/*.log', recursive=False):
            with open(name, 'r') as f:
                print('***** %s ***** ' % name)
                lines = f.readlines()
                print(*lines[-n:])
