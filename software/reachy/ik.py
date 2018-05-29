from numpy import deg2rad

from pypot.creatures import ik


class IkChain(object):
    def __init__(self, robot, tip):
        self._chain = ik.IKChain.from_poppy_creature(robot, robot.motors, [], tip=tip)

    @property
    def joints_position(self):
        return self._chain.joints_position

    @property
    def end_effector(self):
        return self._chain.end_effector

    def convert_to_ik_angles(self, joints):
        """ Convert to IKPY internal representation. """
        return [0] + [deg2rad(j) for j in joints] + [0]

    def forward_kinematics(self, joints):
        return self._chain.forward_kinematics(self.convert_to_ik_angles(joints))

    def inverse_kinematics(self, target, initial_position=None, accurate=False):
        opt = {}
        if not accurate:
            opt['max_iter'] = 3
        target = self.convert_to_ik_angles(target)
        return self._chain.inverse_kinematics(target, initial_position, **opt)[1:-1]
