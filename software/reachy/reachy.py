import os

from numpy import sum
from functools import partial

from pypot.creatures import AbstractPoppyCreature

from .primitives import (Record, Play,
                         GotoRest, Idle, TiringDemo,
                         TurnCompliant)


class Reachy(AbstractPoppyCreature):
    @classmethod
    def setup(cls, robot):
        robot._primitive_manager._filter = partial(sum, axis=0)

        for m in robot.motors:
            m.moving_speed = 50

        robot.attach_primitive(TiringDemo(robot), 'tiring_demo')
        robot.attach_primitive(TurnCompliant(robot), 'turn_compliant')
        robot.attach_primitive(GotoRest(robot), 'goto_rest')
        robot.attach_primitive(Idle(robot), 'idle')

        robot.attach_primitive(Record(robot), 'record')
        robot.attach_primitive(Play(robot), 'play')

        if robot.simulated:
            vrep_io = robot._controllers[0].io
            robot.is_colliding = lambda: vrep_io.get_collision_state('Collision')


def Leachy(*args, **kwargs):
    config = os.path.join(os.path.dirname(__file__),
                          'configuration', 'leachy.json')

    return Reachy(config=config, *args, **kwargs)
