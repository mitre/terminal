import asyncio

from aioconsole import ainput

from app.objects.c_operation import Operation
from plugins.terminal.app.terminal.zero import Zero
from plugins.terminal.app.utility.console import Console
from plugins.terminal.app.utility.session import Session


class Shell:

    def __init__(self, services):
        self.data_svc = services.get('data_svc')
        self.planning_svc = services.get('planning_svc')
        self.app_svc = services.get('app_svc')
        self.session = Session(services)
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
        return sorted(await self.data_svc.locate('agents'), key=lambda a: a.last_seen)

    async def _show_agents(self):
        hosts = []
        for i, a in enumerate(await self._sorted_agent_list()):
            hosts.append(dict(idx=str(i), host=a.host, user=a.username, priv=a.privilege, paw=a.paw, trusted=a.trusted))
        if not hosts:
            self.console.hint('Deploy 54ndc47 agents to add new hosts')
        await self.console.table(hosts)

    async def _show_sessions(self):
        await self.console.table([dict(idx=s['id'], paw=s['paw']) for s in self.session.sessions])

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
            adv = await self.data_svc.locate('adversaries', match=dict(adversary_id='56aebecf-abca-40c1-ad24-658e7c25b55b'))
            planner = await self.data_svc.locate('planners')
            agents = await self.data_svc.locate('agents', match=dict(group=agent.group))
            op = await self.data_svc.store(
                Operation(id='1000', name='terminal', adversary=adv[0], agents=agents, planner=planner[0],
                          state='running')
            )
            op.set_start_details()
            loop = asyncio.get_event_loop()
            loop.create_task(self.app_svc.run_operation(op))
            self.console.line('Queued. Waiting for agent to beacon...', 'green')
        else:
            self.console.line('No agent found for idx = %s.' % agent_idx, 'red')
