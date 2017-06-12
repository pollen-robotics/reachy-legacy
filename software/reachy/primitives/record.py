import glob

from pypot.primitive import Primitive, LoopPrimitive
from pypot.primitive.move import MoveRecorder, MovePlayer, Move


class Record(LoopPrimitive):
    properties = ['record_name']
    path = '/tmp/{}.json'

    def __init__(self, robot):
        LoopPrimitive.__init__(self, robot, 1)
        self.record_name = "demo_example"

    def setup(self):
        for m in self.robot.joint_motors:
            m.compliant = True

        self.recorder = MoveRecorder(self.robot, 50.0, self.robot.joint_motors)
        self.recorder.start()

    def update(self):
        pass

    def teardown(self):
        self.recorder.stop()

        for m in self.robot.joint_motors:
            m.compliant = False

        with open(self.path.format(self.record_name), 'w') as f:
            self.recorder.move.save(f)


class Play(Primitive):
    properties = ['record_name', 'moves']
    path = '/tmp/{}.json'

    def __init__(self, robot):
        Primitive.__init__(self, robot)
        self.record_name = "demo_example"

    def setup(self):
        for m in self.robot.joint_motors:
            m.compliant = False
            m.moving_speed = 0

    def run(self):
        with open(self.path.format(self.record_name)) as f:
            move = Move.load(f)

        self.player = MovePlayer(self.robot, move, max_start_speed=0)
        self.player.start()
        self.player.wait_to_stop()

    def teardown(self):
        for m in self.robot.joint_motors:
            m.moving_speed = 0

    @property
    def moves(self):
        return [s.replace('/tmp/', '').replace('.json', '')
                for s in glob.glob('/tmp/*.json')]
