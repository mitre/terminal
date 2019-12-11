import random
import string

from shutil import which

from aiohttp_jinja2 import template


class TermService:

    def __init__(self, services, terminal_keys):
        self.file_svc = services.get('file_svc')
        self.auth_svc = services.get('auth_svc')
        self.terminal_keys = terminal_keys

    @template('terminal.html')
    async def splash(self, request):
        await self.auth_svc.check_permissions(request)
        return dict(sessions=[1,1,2,2,3,4])

    async def dynamically_compile(self, headers):
        name, platform = headers.get('file'), headers.get('platform')
        if which('go') is not None:
            plugin, file_path = await self.file_svc.find_file_path(name)

            ldflags = ['-s', '-w', '-X main.key=%s' % self._generate_key()]

            output = 'plugins/%s/payloads/%s-%s' % (plugin, name, platform)
            self.file_svc.log.debug('Dynamically compiling %s' % name)
            await self.file_svc.compile_go(platform, output, file_path, ldflags=' '.join(ldflags))
        return '%s-%s' % (name, platform)

    """ PRIVATE """

    @staticmethod
    def _generate_key(size=30):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(size))
