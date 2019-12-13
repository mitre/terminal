import asyncio

from aioconsole import ainput

from plugins.terminal.app.terminal.zero import Zero
from plugins.terminal.app.utility.console import Console
from plugins.terminal.app.utility.session import Session


class Shell:

    def __init__(self, services):
        self.app_svc = services.get('app_svc')
        self.session = Session(services)
        self.prompt = 'caldera> '
        self.console = Console()

    async def start(self):
        await asyncio.sleep(1)
        while True:
            try:
                cmd = await ainput(self.prompt)
                if cmd:
                    self.app_svc.log.debug(cmd)
                    await self.session.refresh()
                    commands = {
                        'help': lambda _: self._help(),
                        'sessions': lambda _: self._show_sessions(),
                        'join': lambda c: self._connect_session(cmd),
                    }
                    command = [c for c in commands.keys() if cmd.startswith(c)]
                    await commands[command[0]](cmd)
            except Exception as e:
                self.console.line('Bad command {}'.format(e), 'red')

    """ PRIVATE """

    @staticmethod
    async def _help():
        print('HELP MENU:')
        print('Start a session by creating a new operation with the terminal adversary')
        print('-> sessions: show all active sessions')
        print('-> join [n]: connect to a session by ID')

    async def _show_sessions(self):
        await self.console.table([dict(idx=s['id'], paw=s['paw']) for s in self.session.sessions])

    async def _connect_session(self, cmd):
        session = int(cmd.split(' ')[1])
        try:
            conn = next(i['connection'] for i in self.session.sessions if i['id'] == int(session))
            conn.setblocking(True)
            conn.send(str.encode(' '))
            await Zero(conn).enter()
        except StopIteration:
            self.console.line('Session cannot be established with %s' % session, 'red')
