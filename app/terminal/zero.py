from aioconsole import ainput
from termcolor import colored

from plugins.offensive.app.utility.console import Console


class Zero:

    def __init__(self, paw, conn, services):
        self.conn = conn
        self.log = services.get('utility_svc').create_logger('zero-%s' % paw)
        self.console = Console()

    async def enter(self):
        while True:
            cmd = await ainput(colored('zero> ', 'magenta'))
            self.log.debug(cmd)
            if cmd == '?':
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

    async def _execute(self, cmd):
        self.conn.send(str.encode('%s\n' % cmd))
        client_response = str(self.conn.recv(4096), 'utf-8')
        print(client_response, end='')
