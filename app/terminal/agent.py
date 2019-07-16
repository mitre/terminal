from aioconsole import ainput

from plugins.offensive.app.terminal.zero import Zero
from plugins.offensive.app.utility.console import Console


class Agent:

    def __init__(self, services, log, session):
        self.data_svc = services.get('data_svc')
        self.log = log
        self.console = Console()
        self.services = services
        self.session = session

    async def enter(self, paw):
        while True:
            cmd = await ainput('%s> ' % paw)
            commands = {
                '?': lambda _: self._help(),
                'c': lambda p: self._new_zero_shell(p),
                ' ': lambda _: self._do_nothing()
            }
            await commands[cmd](paw)

    """ PRIVATE """

    @staticmethod
    async def _help():
        print('AGENT MODE HELP:')
        print('-> c: connect to the agent session')

    async def _new_zero_shell(self, paw):
        try:
            conn = next(i['connection'] for i in self.session.sessions if i['paw'] == paw)
            conn.setblocking(True)
            conn.send(str.encode(' '))
            await Zero(paw, conn, self.services).enter()
        except StopIteration:
            self.console.line('Session cannot be established with %s' % paw, 'red')

    @staticmethod
    async def _do_nothing():
        pass

