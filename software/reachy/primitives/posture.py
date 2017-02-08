import time
import numpy

from pypot.primitive import Primitive, LoopPrimitive
from pypot.primitive.utils import Sinus


class GotoRest(Primitive):
    properties = ['speed']

    def __init__(self, robot):
        Primitive.__init__(self, robot)
        self.speed = 25

    def run(self):
        for m in self.robot.joint_motors:
            m.compliant = False
            m.moving_speed = self.speed
            m.goal_position = 0

        target = numpy.array([0 for m in self.robot.joint_motors])

        while True:
            current = numpy.array([m.present_position for m in self.robot.joint_motors])

            if numpy.linalg.norm(target - current) < 10:
                break

            time.sleep(0.25)

        for m in self.robot.joint_motors:
            m.compliant = True


class Idle(LoopPrimitive):
    def __init__(self, robot):
        LoopPrimitive.__init__(self, robot, 1.0)

    def setup(self):
        for m in self.robot.joint_motors:
            m.compliant = False

        pos = {m.name: 0 for m in self.robot.joint_motors}
        pos['elbow_pitch'] = 30
        self.robot.goto_position(pos, 2.0, wait=True)

        for m in self.robot.joint_motors:
            m.moving_speed = 50.0

        for m in [self.robot.wrist_pitch, self.robot.wrist_roll]:
            m.compliant = True

        self.sinus = [
            Sinus(self.robot, 50.0, [self.robot.elbow_pitch], amp=15, freq=0.25, offset=30),
            Sinus(self.robot, 50.0, [self.robot.shoulder_roll], amp=10, freq=0.1, offset=10),
            Sinus(self.robot, 50.0, [self.robot.arm_yaw], amp=3, freq=0.12)
        ]

        for s in self.sinus:
            s.start()

    def update(self):
        pass

    def teardown(self):
        for s in self.sinus:
            s.stop()

        self.robot.elbow_pitch.moving_speed = 25
        self.robot.elbow_pitch.goal_position = 0

        time.sleep(2)
        for m in self.robot.motors:
            m.compliant = True
