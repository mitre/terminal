from plugins.offensive.app.utility.console import Console
from plugins.offensive.app.utility.resource_svc import ResourceService


class Agent:

    def __init__(self, services, log):
        self.data_svc = services.get('data_svc')
        self.log = log
        self.resource_service = ResourceService(services)
        self.console = Console()

    async def enter(self, paw, cmd):
        try:
            if cmd == '?':
                await self.help()
            elif cmd == 'i':
                agent = await self.data_svc.dao.get('core_agent', dict(paw=paw))
                instructions = await self.data_svc.dao.get('core_chain', dict(id=agent[0]['id']))
                self.console.table(instructions)
            elif cmd.startswith('rc'):
                await self.resource_service.save(paw, cmd.split(' ')[1])
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
        print('-> i: list all the uncollected instructions')
        print('-> rc [n]: give a connected agent a resource file to run')

