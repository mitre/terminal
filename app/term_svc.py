import hashlib
import random
import string
from shutil import which


class TermService:

    def __init__(self, services, default_key="MY3DUY6IVC5LN956Q4KUEQEZ2TRQL9"):
        self.file_svc = services.get('file_svc')
        self.agent_svc = services.get('agent_svc')

        # TODO: move to database
        self._keys_by_hash = dict()
        self._keys_by_hash[hashlib.sha256(default_key.encode()).digest()] = default_key

    async def dynamically_compile(self, headers):
        name, platform = headers.get('file'), headers.get('platform')
        if which('go') is not None:
            plugin, file_path = await self.file_svc.find_file_path(name)

            ldflags = ['-s', '-w', '-X main.key=%s' % (self._generate_key(),)]
            for param in ('defaultServer', 'defaultGroup', 'defaultSleep'):
                if param in headers:
                    ldflags.append('-X main.%s=%s' % (param, headers[param]))

            output = 'plugins/%s/payloads/%s-%s' % (plugin, name, platform)
            self.file_svc.log.debug('Dynamically compiling %s' % name)
            await self.file_svc.compile_go(platform, output, file_path, ldflags=' '.join(ldflags))
        return '%s-%s' % (name, platform)

    """ PRIVATE """

    def _generate_key(self, size=30):
        key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(size))
        self._track_key(key)
        return key

    def _track_key(self, key):
        self._keys_by_hash[hashlib.sha256(key.encode()).digest()] = key

    def validate_key(self, key_hash):
        if key_hash in  self._keys_by_hash:
            return True
        else:
            return False
