import asyncio

from aioconsole import ainput

from app.objects.c_link import Link
from app.objects.c_operation import Operation
from plugins.terminal.app.terminal.zero import Zero
from plugins.terminal.app.utility.console import Console
from plugins.terminal.app.utility.session import Session


class Shell:

    def __init__(self, services):
        self.data_svc = services.get('data_svc')
        self.planning_svc = services.get('planning_svc')
        self.app_svc = services.get('app_svc')
        self.agent_svc = services.get('agent_svc')
        self.session = Session(services, self.app_svc.log)
        self.prompt = 'caldera> '
        self.console = Console()

    async def start(self):
        await asyncio.sleep(1)
        while True:
            try:
                cmd = await ainput(self.prompt)
                if cmd:
                    self.app_svc.log.debug(cmd)
                    await self.session.refresh()
                    commands = {
                        'help': lambda _: self._help(),
                        'hosts': lambda _: self._show_hosts(),
                        'sessions': lambda _: self._show_sessions(),
                        'join': lambda c: self._connect_session(cmd),
                        'new': lambda c: self._new_session(cmd)
                    }
                    command = [c for c in commands.keys() if cmd.startswith(c)]
                    await commands[command[0]](cmd)
            except Exception:
                self.console.line('Bad command', 'red')

    """ PRIVATE """

    @staticmethod
    async def _help():
        print('HELP MENU:')
        print('-> hosts: show all connected computers')
        print('-> sessions: show all active sessions')
        print('-> new [n]: start a new session on an agent ID')
        print('-> join [n]: connect to a session by ID')

    async def _show_hosts(self):
        hosts = []
        for a in await self.data_svc.locate('agents'):
            hosts.append(dict(paw=a.paw))
        if not hosts:
            self.console.hint('Deploy 54ndc47 agents to add new hosts')
        await self.console.table(hosts)

    async def _show_sessions(self):
        await self.console.table(self.session.sessions)

    async def _connect_session(self, cmd):
        session = int(cmd.split(' ')[1])
        try:
            conn = next(i['connection'] for i in self.session.sessions if i['id'] == int(session))
            conn.setblocking(True)
            conn.send(str.encode(' '))
            await Zero(conn).enter()
        except StopIteration:
            self.console.line('Session cannot be established with %s' % session, 'red')

    async def _new_session(self, command):
        agent_id = command.split(' ')[1]
        agent = await self.data_svc.locate('agents', match=dict(paw=agent_id))
        if agent:
            match = dict(ability_id='356d1722-7784-40c4-822b-0cf864b0b36d', platform=agent[0].platform)
            abilities = await self.data_svc.locate('abilities', match=match)
            abilities = await agent[0].capabilities(abilities)
            command = self.planning_svc.decode(abilities[0].test, agent[0], group='')
            if abilities[0].cleanup:
                cleanup = self.planning_svc.decode(abilities[0].cleanup, agent[0], group='')
            else:
                cleanup = ''

            agents = await self.data_svc.locate('agents', match=dict(group=agent[0].group))
            op = await self.data_svc.store(
                Operation(id='1000', name='terminal', adversary=None, agents=agents)
            )
            op.set_start_details()
            op.add_link(
                Link(command=self.app_svc.encode_string(command), paw=agent[0].paw, score=0, jitter=0,
                     ability=abilities[0], operation=op.id, cleanup=self.app_svc.encode_string(cleanup))
            )
            self.console.line('Queued. Waiting for agent to beacon...', 'green')
        else:
            self.console.line('No agent with an ID = %s' % agent_id, 'red')
