import time

from pypot.primitive import Primitive
from pypot.primitive.move import Move, MovePlayer


class Handshake(Primitive):
    properties = ['speed']

    def __init__(self, robot):
        Primitive.__init__(self, robot)
        self.speed = 25

    def setup(self):
        with open('/home/poppy/dev/puppet-master/handshake_1.record') as f:
            self.h1 = Move.load(f)

        with open('/home/poppy/dev/puppet-master/handshake_2.record') as f:
            self.h2 = Move.load(f)

    def run(self):
        for m in self.robot.joint_motors:
            m.moving_speed = self.speed

        self.player = MovePlayer(self.robot, self.h1)
        self.player.start()
        self.player.wait_to_stop()

        while self.robot.wrist_pitch.present_load < 0:
            time.sleep(0.2)

        self.player = MovePlayer(self.robot, self.h2)
        self.player.start()
        self.player.wait_to_stop()

        self.robot.goto_rest.start()
        self.robot.goto_rest.wait_to_stop()


class Check(Primitive):
    properties = ['speed']

    def __init__(self, robot):
        Primitive.__init__(self, robot)
        self.speed = 25

    def setup(self):
        with open('/home/poppy/dev/puppet-master/handshake_1.record') as f:
            self.h1 = Move.load(f)

        with open('/home/poppy/dev/puppet-master/check_1.record') as f:
            self.h2 = Move.load(f)

    def run(self):
        for m in self.robot.joint_motors:
            m.moving_speed = self.speed

        self.player = MovePlayer(self.robot, self.h1)
        self.player.start()
        self.player.wait_to_stop()

        time.sleep(1)

        while self.robot.shoulder_roll.present_load < 8:
            time.sleep(0.2)

        self.player = MovePlayer(self.robot, self.h2)
        self.player.start()
        self.player.wait_to_stop()

        self.robot.goto_rest.start()
        self.robot.goto_rest.wait_to_stop()
