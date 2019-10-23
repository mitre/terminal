import asyncio
from datetime import datetime

from aioconsole import ainput

from plugins.terminal.app.terminal.zero import Zero
from plugins.terminal.app.utility.console import Console
from plugins.terminal.app.utility.session import Session


class Shell:

    def __init__(self, services):
        self.data_svc = services.get('data_svc')
        self.planning_svc = services.get('planning_svc')
        self.plugin_svc = services.get('plugin_svc')
        self.agent_svc = services.get('agent_svc')
        self.session = Session(services, self.plugin_svc.log)
        self.prompt = 'caldera> '
        self.console = Console()

    async def start(self):
        await asyncio.sleep(1)
        while True:
            try:
                cmd = await ainput(self.prompt)
                if cmd:
                    self.plugin_svc.log.debug(cmd)
                    await self.session.refresh()
                    commands = {
                        'help': lambda _: self._help(),
                        'hosts': lambda _: self._show_hosts(),
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
        print('-> new [n]: start a new session on an agent ID')
        print('-> join [n]: connect to a session by ID')

    async def _show_hosts(self):
        agents = await self.data_svc.explode('agent')
        sessions = self.session.sessions
        hosts = []
        for paw in set([x['paw'] for x in agents + sessions]):
            temp_sessions = [s['id'] for s in sessions if s['paw'] == paw]
            temp_agents = [a['id'] for a in agents if a['paw'] == paw]
            hosts.append(dict(paw=paw, agents=temp_agents, sessions=temp_sessions))
        if not hosts:
            self.console.hint('Deploy 54ndc47 agents to add new hosts')
        await self.console.table(hosts)

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
        agent = await self.data_svc.explode('agent', criteria=dict(id=agent_id))
        if agent:
            abilities = await self.data_svc.explode('ability',
                                                    criteria=dict(ability_id='356d1722-7784-40c4-822b-0cf864b0b36d',
                                                                  platform=agent[0]['platform'])
                                                    )
            abilities = await self.agent_svc.capable_agent_abilities(abilities, agent[0])
            command = await self.planning_svc.decode(abilities[0]['test'], agent[0], group='')
            cleanup = self.planning_svc.decode(abilities[0].get('cleanup', ''), agent[0], group='')

            link = dict(op_id=None, paw=agent[0]['paw'], ability=abilities[0]['id'], jitter=0, score=0,
                        decide=datetime.now(), command=self.plugin_svc.encode_string(command),
                        cleanup=self.plugin_svc.encode_string(cleanup), executor=abilities[0]['executor'])
            await self.data_svc.save('link', link)
            self.console.line('Queued. Waiting for agent to beacon...', 'green')
        else:
            self.console.line('No agent with an ID = %s' % agent_id, 'red')
