from app.objects.c_c2 import C2
from plugins.terminal.app.terminal.shell import Shell

import asyncio


class TCPSocket(C2):

    def __init__(self, services, module, config, name):
        self.port = config['port']
        self.services = services
        super().__init__(services, module, config, name)

    def start(self, app):
        loop = asyncio.get_event_loop()
        terminal = self._start_terminal(loop, self.services)
        self._start_socket_listener(loop, terminal)

    def valid_config(self):
        """
        Overriding of super class function. Checks that the tcp port number X is 1023 < X < 65535
        :return:
        """
        if self.port < 1023:
            self.log.error('Choose a tcp port greater than 1023 to listen on')
            return False
        elif self.port > 65535:
            self.log.error('Choose valid tcp port number to listen on')
            return False
        return True

    """ PRIVATE """

    @staticmethod
    def _start_terminal(loop, services):
        terminal = Shell(services)
        loop.create_task(terminal.start())
        return terminal

    def _start_socket_listener(self, loop, terminal):
        for sock in [self.port]:
            print('...Reverse-shell listener opened on port %s' % sock)
            h = asyncio.start_server(terminal.session.accept, '0.0.0.0', sock, loop=loop)
            loop.create_task(h)
