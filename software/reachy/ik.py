from numpy import deg2rad, rad2deg

from ikpy.chain import Chain


class IkChain(object):
    def __init__(self, robot, tip):
        self._chain = Chain.from_urdf_file(robot.urdf_file,
                                           base_elements=['base'],
                                           last_link_vector=tip)
        self._robot = robot

    @property
    def joints_position(self):
        return [m.present_position for m in self._robot.motors]

    @property
    def end_effector(self):
        return self.forward_kinematics(self.joints_position)[:3, 3]

    def convert_to_ik_angles(self, joints):
        """ Convert to IKPY internal representation. """
        return [0] + [deg2rad(j) for j in joints] + [0]

    def convert_from_ik_angles(self, joints):
        return [rad2deg(j) for j in joints][1:-1]

    def forward_kinematics(self, joints):
        return self._chain.forward_kinematics(self.convert_to_ik_angles(joints))

    def inverse_kinematics(self, target, initial_position=None, accurate=False):
        opt = {}
        if not accurate:
            opt['max_iter'] = 3

        if initial_position is not None:
            initial_position = self.convert_to_ik_angles(initial_position)
        joints = self._chain.inverse_kinematics(target, initial_position, **opt)
        joints = self.convert_from_ik_angles(joints)

        return joints
