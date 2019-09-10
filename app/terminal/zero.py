from aioconsole import ainput
from termcolor import colored

from plugins.terminal.app.utility.console import Console


class Zero:

    def __init__(self, conn):
        self.conn = conn
        self.console = Console()

    async def enter(self):
        self.console.hint('You can enter "help" here as well')
        while True:
            cmd = await ainput(colored('zero> ', 'magenta'))
            if cmd == 'help':
                await self._help()
            elif cmd == 'bg':
                break
            elif len(str.encode(cmd)) > 0:
                await self._execute(cmd)

    """ PRIVATE """

    @staticmethod
    async def _help():
        print('ZERO SHELL HELP:')
        print('-> bg: send this shell to the background')
        print('-> download [filename]: drop any file from the API')
        print('-> upload [filename]: exfil any file or archive to the API')

    async def _execute(self, cmd):
        self.conn.send(str.encode('%s\n' % cmd))
        client_response = str(self.conn.recv(4096), 'utf-8')
        print(client_response, end='')
