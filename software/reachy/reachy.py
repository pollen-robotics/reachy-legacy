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

from .fullreachy import full_reachy
from .primitives import (GotoRest, Idle, TiringDemo,
                         TurnCompliant)
from .ik import IkChain


tips = {
    'none': [0, 0, -0.02409],
    'hand': [0.04, 0, -0.23],
    'brunel_hand': [0.0, 0.0, -0.1],
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
    def __new__(cls, *args, **kwargs):
        if 'brunel_hand' in kwargs:
            # This means we are a Leachy
            if 'config' in kwargs:
                config = kwargs['config']
                config = config.replace('.json', '_hand.json')
            else:
                config = os.path.join(os.path.dirname(__file__),
                                      'configuration',
                                      'reachy_hand.json')
            kwargs['config'] = config

        robot = AbstractPoppyCreature.__new__(cls, *args, **kwargs)

        if 'brunel_hand' in kwargs:
            from brunel_hand import BrunelHand

            port = kwargs.pop('brunel_hand')
            hand = BrunelHand(port)
            robot.hand = hand
            robot.hand.open()

        if 'luos_extension' in kwargs:
            from pyluos import Robot as LuosExtension

            port = kwargs.pop('luos_extension')
            ext = LuosExtension(port)

            for m in ext.modules:
                setattr(robot, m.alias, m)

            robot.luos_extension = ext.modules

        return robot

    @classmethod
    def setup(cls, robot):
        setup(robot)
        if robot.motors[0].name.startswith('r'):
            robot.ik_chain = IkChain(robot, tip=[0, 0, -0.02409])


def Leachy(*args, **kwargs):
    if 'simulator' not in kwargs:
        if 'config' not in kwargs:
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

    if 'brunel_hand' in kwargs:
        robot.urdf_file = robot.urdf_file.replace('leachy.urdf', 'leachy_hand.urdf')
        robot.ik_chain = IkChain(robot, tip=tips['brunel_hand'])
    else:
        robot.ik_chain = IkChain(robot, tip=tips['hand'])
    return robot


class FullReachy(object):
    def __init__(self, left_brunel_hand, right_brunel_hand):
        config_file = os.path.join(os.path.dirname(__file__),
                                   'configuration', 'fullreachy.json')
        self._robot, self.reachy, self.leachy, self.head = full_reachy(config_file)

        self.reachy.urdf_file = os.path.join(os.path.dirname(__file__), 'reachy_hand.urdf')
        self.reachy.ik_chain = IkChain(self.reachy, tip=tips['brunel_hand'])

        self.leachy.urdf_file = os.path.join(os.path.dirname(__file__), 'leachy_hand.urdf')
        self.leachy.ik_chain = IkChain(self.leachy, tip=tips['brunel_hand'])

        from brunel_hand import BrunelHand

        self.leachy.hand = BrunelHand(left_brunel_hand)
        self.leachy.hand.open()

        self.reachy.hand = BrunelHand(right_brunel_hand)
        self.reachy.hand.open()

    @property
    def motors(self):
        return self.reachy.motors + self.leachy.motors + self.head.motors

    def goto_position(self,
                      position_for_motors, duration,
                      control=None, wait=False):
        self._robot.goto_position(
            position_for_motors=position_for_motors,
            duration=duration,
            control=control,
            wait=wait
        )