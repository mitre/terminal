from plugins.offensive.app.terminal.zero import Zero
from plugins.offensive.app.utility.console import Console


class Agent:

    def __init__(self, services, log, session):
        self.data_svc = services.get('data_svc')
        self.log = log
        self.console = Console()
        self.services = services
        self.session = session

    async def enter(self, paw, cmd):
        try:
            if cmd == '?':
                await self.help()
            elif cmd == 'c':
                conn = next(i['connection'] for i in self.session.sessions if i['paw'] == paw)
                conn.setblocking(True)
                conn.send(str.encode(' '))
                await Zero(conn, self.services).enter()
            elif cmd == '':
                pass
            else:
                self.console.line('Bad command - are you sure?', 'red')
        except IndexError:
            self.console.line('No results found', 'red')
        except Exception as e:
            self.console.line('Command not available: %s' % e, 'red')

    @staticmethod
    async def help():
        print('AGENT MODE HELP:')
        print('-> c: connect to the agent')
