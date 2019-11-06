import random
import string

from shutil import which


class TermService:

    def __init__(self, file_svc, default_terminal_key='94699f9970213dd1d4054ca678f1278a'):
        self.file_svc = file_svc
        self.app_svc = file_svc.get_service('app_svc')

        if which('go'):
            self.terminal_key = self.app_svc.config.get('terminal_key', default_terminal_key)
        elif 'terminal_key' in self.app_svc.config:
            file_svc.log.warning(
                '[terminal plugin] Unable to locate golang compiler. Custom terminal_key value will not be used.')
            self.terminal_key = default_terminal_key
        else:
            self.terminal_key = default_terminal_key

    async def dynamically_compile(self, headers):
        name, platform = headers.get('file'), headers.get('platform')
        if which('go') is not None:
            plugin, file_path = await self.file_svc.find_file_path(name)

            ldflags = ['-s', '-w',
                       '-X main.key=%s' % self._generate_key(),
                       '-X main.terminal_key=%s' % self.terminal_key,
                       ]

            output = 'plugins/%s/payloads/%s-%s' % (plugin, name, platform)
            self.file_svc.log.debug('Dynamically compiling %s' % name)
            await self.file_svc.compile_go(platform, output, file_path, ldflags=' '.join(ldflags))
        return '%s-%s' % (name, platform)

    """ PRIVATE """

    @staticmethod
    def _generate_key(size=30):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(size))
