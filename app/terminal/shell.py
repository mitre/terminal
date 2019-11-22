import asyncio
import traceback

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
                        'agents': lambda _: self._show_agents(),
                        'sessions': lambda _: self._show_sessions(),
                        'join': lambda c: self._connect_session(cmd),
                        'new': lambda c: self._new_session(cmd)
                    }
                    command = [c for c in commands.keys() if cmd.startswith(c)]
                    await commands[command[0]](cmd)
            except Exception as e:
                if self.app_svc.config.get('debug'):
                    traceback.print_exc()
                self.console.line('Bad command {}'.format(e), 'red')

    """ PRIVATE """

    @staticmethod
    async def _help():
        print('HELP MENU:')
        print('-> agents: show all connected computers')
        print('-> sessions: show all active sessions')
        print('-> new [n]: start a new session on an agent idx')
        print('-> join [n]: connect to a session by ID')

    async def _sorted_agent_list(self):
        return sorted(await self.data_svc.locate('agents'), key=lambda a: a.created)

    async def _show_agents(self):
        hosts = []
        for i, a in enumerate(await self._sorted_agent_list()):
            hosts.append(dict(idx=str(i), host=a.host, user=a.username, priv=a.privilege, paw=a.paw))
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
        agent_idx = int(command.split(' ')[1])
        agent = (await self._sorted_agent_list())[agent_idx]
        if agent:
            match = dict(ability_id='356d1722-7784-40c4-822b-0cf864b0b36d', platform=agent.platform)
            abilities = await self.data_svc.locate('abilities', match=match)
            abilities = await agent.capabilities(abilities)
            command = self.planning_svc.decode(abilities[0].test, agent, group='')
            if abilities[0].cleanup:
                cleanup = self.planning_svc.decode(abilities[0].cleanup, agent, group='')
            else:
                cleanup = ''

            agents = await self.data_svc.locate('agents', match=dict(group=agent.group))
            op = await self.data_svc.store(
                Operation(id='1000', name='terminal', adversary=None, agents=agents)
            )
            op.set_start_details()
            op.add_link(
                Link(command=self.app_svc.encode_string(command), paw=agent.paw, score=0, jitter=0,
                     ability=abilities[0], operation=op.id, cleanup=self.app_svc.encode_string(cleanup))
            )
            self.console.line('Queued. Waiting for agent to beacon...', 'green')
        else:
            self.console.line('No agent found for idx = %s.' % agent_idx, 'red')
