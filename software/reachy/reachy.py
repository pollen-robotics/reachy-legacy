from numpy import sum
from functools import partial

from pypot.creatures import AbstractPoppyCreature

from .primitives import (Grasp, Release,
                         Record, Play,
                         Handshake, Check,
                         GotoRest, Idle, TiringDemo,
                         TurnCompliant)


class Reachy(AbstractPoppyCreature):
    @classmethod
    def setup(cls, robot):
        robot._primitive_manager._filter = partial(sum, axis=0)

        robot.joint_motors = [m for m in robot.motors if m.name != 'finger_grip']
        for m in robot.motors:
            m.moving_speed = 50

        robot.finger_grip.goal_position = -100

        # robot.attach_primitive(Grasp(robot), 'grasp')
        # robot.attach_primitive(Release(robot), 'release')

        robot.attach_primitive(TiringDemo(robot), 'tiring_demo')
        robot.attach_primitive(TurnCompliant(robot), 'turn_compliant')
        robot.attach_primitive(GotoRest(robot), 'goto_rest')
        robot.attach_primitive(Idle(robot), 'idle')

        robot.attach_primitive(Handshake(robot), 'handshake')
        robot.attach_primitive(Check(robot), 'check')

        robot.attach_primitive(Record(robot), 'record')
        robot.attach_primitive(Play(robot), 'play')
