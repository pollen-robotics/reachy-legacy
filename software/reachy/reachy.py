import os
import json
import time

from numpy import sum
from threading import Thread
from functools import partial
from collections import deque

from pypot.utils import pypot_time
from pypot.creatures import AbstractPoppyCreature
from pypot.vrep import from_vrep, VrepConnectionError

from .primitives import (Record, Play,
                         GotoRest, Idle, TiringDemo,
                         TurnCompliant)
from .ik import IkChain


tips = {
    'none': [0, 0, -0.02409],
    'hand': [0.04, 0, -0.23],
}


def setup(robot):
    robot._primitive_manager._filter = partial(sum, axis=0)

    for m in robot.motors:
        m.moving_speed = 50

    for m in robot.motors:
        # make alias without the r_ or l_ prefix in motor name
        name = m.name[2:]
        setattr(robot, name, m)

    robot.attach_primitive(TiringDemo(robot), 'tiring_demo')
    robot.attach_primitive(TurnCompliant(robot), 'turn_compliant')
    robot.attach_primitive(GotoRest(robot), 'goto_rest')
    robot.attach_primitive(Idle(robot), 'idle')

    robot.attach_primitive(Record(robot), 'record')
    robot.attach_primitive(Play(robot), 'play')

    if robot.simulated:
        vrep_io = robot._controllers[0].io
        robot.is_colliding = lambda: vrep_io.get_collision_state('Collision')

        robot.last_collision = None
        robot.recent_collisions = deque([], 10)

        def did_collide():
            while True:
                if robot.is_colliding():
                    t = pypot_time.time()
                    robot.last_collision = t
                    robot.recent_collisions.append(t)
                time.sleep(0.02)

        t = Thread(target=did_collide)
        t.daemon = True
        t.start()


class Reachy(AbstractPoppyCreature):
    @classmethod
    def setup(cls, robot):
        setup(robot)
        if robot.motors[0].name.startswith('r'):
            robot.ik_chain = IkChain(robot, tip=[0, 0, -0.02409])


def Leachy(*args, **kwargs):
    if 'config' not in kwargs and 'simulator' not in kwargs:
        config = os.path.join(os.path.dirname(__file__),
                              'configuration', 'leachy.json')
        kwargs['config'] = config
        robot = Reachy(*args, **kwargs)

    if 'simulator' in kwargs:
        config = os.path.join(os.path.dirname(__file__),
                              'configuration', 'leachy.json')

        if 'scene' not in kwargs:
            kwargs['scene'] = 'leachy.ttt'
        if kwargs['scene'] == 'keep-existing':
            scene = None
        else:
            scene = os.path.join(os.path.dirname(__file__),
                                 'vrep-scene', kwargs['scene'])

        try:
            id = kwargs['id'] if 'id' in kwargs else None
            shared_vrep_io = kwargs['shared_vrep_io'] if 'shared_vrep_io' in kwargs else None
            robot = from_vrep(config, '127.0.0.1', 19997, scene, shared_vrep_io=shared_vrep_io, id=id)
        except VrepConnectionError:
            raise IOError('Connection to V-REP failed!')

        robot.simulated = True
        with open(config) as f:
            robot.config = json.load(f)
        urdf_file = os.path.join(os.path.dirname(__file__), 'leachy.urdf')
        robot.urdf_file = urdf_file
        setup(robot)

    robot.urdf_file = robot.urdf_file.replace('reachy.urdf', 'leachy.urdf')
    robot.ik_chain = IkChain(robot, tip=tips['hand'])
    return robot
