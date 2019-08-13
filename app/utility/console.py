from termcolor import colored


class Console:

    def __init__(self):
        self.console_colors = dict(red=lambda msg: print(colored('[-] %s' % msg, 'red')),
                                   green=lambda msg: print(colored('[+] %s' % msg, 'green')),
                                   cyan=lambda msg: print(colored('[HINT] %s' % msg, 'cyan')),
                                   yellow=lambda msg: print(colored(msg, 'yellow')))

    def line(self, msg, color='green'):
        self.console_colors[color](msg)

    def hint(self, msg, color='cyan'):
        self.console_colors[color](msg)

    async def table(self, data):
        if data:
            headers = list(data[0].keys())
            header_list = [headers]
            for item in data:
                header_list.append([str(item[col] or '') for col in headers])
            column_size = [max(map(len, col)) for col in zip(*header_list)]
            row_format = ' | '.join(['{{:<{}}}'.format(i) for i in column_size])
            header_list.insert(1, ['-' * i for i in column_size])
            await self._print_table(header_list, row_format)

    """ PRIVATE """

    @staticmethod
    async def _print_table(header_list, row_format):
        for item in header_list:
            print(row_format.format(*item))
