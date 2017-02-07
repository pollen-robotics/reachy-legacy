from numpy import sum
from functools import partial

from pypot.creatures import AbstractPoppyCreature



class Reachy(AbstractPoppyCreature):
    @classmethod
    def setup(cls, robot):
        robot._primitive_manager._filter = partial(sum, axis=0)

        robot.joint_motors = [m for m in robot.motors if m.name != 'finger_grip']
        for m in robot.joint_motors:
            m.moving_speed = 50

        robot.finger_grip.goal_position = 0
        robot.finger_grip.moving_speed = 0
