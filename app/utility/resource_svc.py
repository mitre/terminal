
class ResourceService:
    
    def __init__(self, services):
        self.log = services.get('utility_svc').create_logger('resource_service')
        self.data_svc = services.get('data_svc')

    async def read(self, name):
        self.log.debug('Reading resource (%s)' % name)
        commands = []
        with open('resources/%s.rc' % name) as f:
            for line in f:
                commands.append(line.replace('\n', ''))
        return commands

    async def save(self, paw, name):
        self.log.debug('Saving resource (%s) into (%s)' % (name, paw))
        with open('resources/%s.rc' % name) as f:
            for line in f:
                command = line.replace('\n', '')
                await self.data_svc.dao.create('instruction', dict(paw=paw, command=command))
