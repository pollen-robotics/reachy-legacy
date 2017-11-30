from numpy import mean
from collections import deque

from pypot.primitive import LoopPrimitive


class TurnCompliant(LoopPrimitive):
    def __init__(self, robot):
        LoopPrimitive.__init__(self, robot, 50.0)
        self.motors = [self.robot.arm_yaw]

    def setup(self):
        for m in self.motors:
            m.torque_limit = 20

        freq = 1.0 / self.period
        self.torque = deque([0], 0.2 * freq)

    def update(self):
        self.torque.append(max([abs(m.present_load) for m in self.motors]))

        mt = mean(self.torque)

        if mt >= 10:
            for m in self.robot.motors:
                m.compliant = True
        elif mt < 4:
            for m in self.robot.motors:
                m.compliant = False
