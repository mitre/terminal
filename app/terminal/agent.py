from aioconsole import ainput
from datetime import datetime

from app.service.planning_svc import PlanningService
from plugins.offensive.app.terminal.zero import Zero
from plugins.offensive.app.utility.console import Console


class Agent:

    def __init__(self, services, log, session):
        self.data_svc = services.get('data_svc')
        self.utility_svc = services.get('utility_svc')
        self.planning_svc = PlanningService(self.data_svc, self.utility_svc)
        self.log = log
        self.console = Console()
        self.session = session

    async def enter(self, host_id):
        agent = await self.data_svc.dao.get('core_agent', dict(id=host_id))
        while True:
            cmd = await ainput('agent-#%s> ' % host_id)
            commands = {
                '?': lambda a,_: self._help(),
                'c': lambda a,_: self._new_zero_shell(a),
                'q': lambda a,c: self._queue_ability(a, c)
            }
            command = [c for c in commands.keys() if not cmd or cmd.startswith(c)]
            await commands[command[0]](agent[0], cmd)

    """ PRIVATE """

    @staticmethod
    async def _help():
        print('AGENT MODE HELP:')
        print('-> q: queue an ability for the agent')
        print('-> c: connect to the agent session')

    async def _new_zero_shell(self, agent):
        try:
            conn = next(i['connection'] for i in self.session.sessions if i['paw'] == agent['paw'])
            conn.setblocking(True)
            conn.send(str.encode(' '))
            await Zero(agent['paw'], conn, self.utility_svc).enter()
        except StopIteration:
            self.console.line('Session cannot be established with %s' % agent['paw'], 'red')

    async def _queue_ability(self, agent, command):
        ability_id = command.split(' ')[1]
        abilities = await self.data_svc.explode_abilities(criteria=dict(id=ability_id))

        command = await self.planning_svc.decode(abilities[0]['test'], agent, group='')
        cleanup = await self.planning_svc.decode(abilities[0].get('cleanup', ''), agent, group='')

        link = dict(op_id=None, host_id=agent['id'], ability=abilities[0]['id'], jitter=0, score=0,
                    decide=datetime.now(), command=self.utility_svc.encode_string(command),
                    cleanup=self.utility_svc.encode_string(cleanup))
        await self.data_svc.dao.create('core_chain', link)
        self.console.line('Ability queued', 'green')
