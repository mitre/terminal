import asyncio
import hashlib
import random
import string
from shutil import which


class TermService:

    def __init__(self, services, default_key="MY3DUY6IVC5LN956Q4KUEQEZ2TRQL9"):
        self.file_svc = services.get('file_svc')
        self.agent_svc = services.get('agent_svc')
        self.data_svc = services.get('data_svc')

        asyncio.get_event_loop().create_task(self._track_key(default_key))

    async def dynamically_compile(self, headers):
        name, platform = headers.get('file'), headers.get('platform')
        if which('go') is not None:
            plugin, file_path = await self.file_svc.find_file_path(name)

            ldflags = ['-s', '-w', '-X main.key=%s' % (await self._generate_key(),)]
            for param in ('defaultServer', 'defaultGroup', 'defaultSleep'):
                if param in headers:
                    ldflags.append('-X main.%s=%s' % (param, headers[param]))

            output = 'plugins/%s/payloads/%s-%s' % (plugin, name, platform)
            self.file_svc.log.debug('Dynamically compiling %s' % name)
            await self.file_svc.compile_go(platform, output, file_path, ldflags=' '.join(ldflags))
        return '%s-%s' % (name, platform)

    """ PRIVATE """

    async def _generate_key(self, size=30):
        key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(size))
        await self._track_key(key)
        return key

    async def _track_key(self, key):
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return await self.data_svc.create('terminal_key', dict(key_hash=key_hash, key=key))

    async def validate_key_hash(self, key_hash):
        res = await self.data_svc.get('terminal_key', dict(key_hash=key_hash.hex()))
        if res:
            return True
        else:
            return False
