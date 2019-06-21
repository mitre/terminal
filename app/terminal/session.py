import socket

from plugins.offensive.app.terminal.zero import Zero
from plugins.offensive.app.utility.console import Console


class Session:

    def __init__(self, services, log):
        self.log = log
        self.services = services
        self.sessions = []
        self.console = Console()

    async def enter(self, index, cmd):
        try:
            if cmd == '?':
                await self.help()
            elif cmd == 'c':
                conn = self.sessions[index]
                conn.send(str.encode(' '))
                await Zero(conn, self.services).enter()
            elif cmd == '':
                pass
            else:
                self.console.line('Bad command - are you sure?', 'red')
        except IndexError:
            self.console.line('No results found', 'red')
        except Exception as e:
            self.console.line('Command failed: %s' % e, 'red')

    @staticmethod
    async def help():
        print('SESSION MODE HELP:')
        print('-> c: connect to the session')

    async def accept(self, reader, writer):
        connection = writer.get_extra_info('socket')
        connection.setblocking(True)
        self.sessions.append(connection)
        self.console.line('New session: %s' % str(connection.getsockname()))

    async def show(self):
        active = []
        for i, conn in enumerate(self.sessions):
            try:
                conn.send(str.encode(' '))
                active.append(dict(index=i, address=str(self.sessions[i].getsockname())))
            except socket.error:
                del self.sessions[i]
        self.console.table(active)
