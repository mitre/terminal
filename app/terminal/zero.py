from aioconsole import ainput
from termcolor import colored

from plugins.offensive.app.utility.console import Console


class Zero:

    def __init__(self, conn, services):
        self.conn = conn
        self.log = services.get('utility_svc').create_logger('zero-%s-%s' % (str(conn.getsockname()[0]), str(conn.getsockname()[1])))
        self.console = Console()

    async def enter(self):
        while True:
            try:
                cmd = await ainput(colored('zero> ', 'magenta'))
                if cmd == '?':
                    await self.help()
                elif cmd == 'bg':
                    break
                elif len(str.encode(cmd)) > 0:
                    await self.execute(cmd)
            except Exception as e:
                self.console.line('Connection was dropped: %s' % e, 'red')
                break

    @staticmethod
    async def help():
        print('ZERO SHELL HELP:')
        print('-> bg: send this shell to the background')

    async def execute(self, cmd):
        self.log.debug('zero> %s' % cmd)
        self.conn.send(str.encode('%s\n' % cmd))
        client_response = str(self.conn.recv(4096), 'utf-8')
        print(client_response, end='')
