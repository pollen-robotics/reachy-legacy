from pypot.robot import from_json


class RobotSubPart(object):
    def __init__(self, robot, motors):
        self._robot = robot
        self.motors = motors

        for m in self.motors:
            setattr(self, m.name, m)

            if m.name.startswith('r_') or m.name.startswith('l_'):
                setattr(self, m.name[2:], m)

    def goto_position(self,
                      position_for_motors, duration,
                      control=None, wait=False):
        self._robot.goto_position(
            position_for_motors=position_for_motors,
            duration=duration,
            control=control,
            wait=wait
        )


def full_reachy(config_file):
    robot = from_json(config_file)

    motors = {
        'reachy': [],
        'leachy': [],
        'head': [],
    }

    for m in robot.motors:
        if m.name.startswith('r_'):
            motors['reachy'].append(m)
        elif m.name.startswith('l_'):
            motors['leachy'].append(m)
        else:
            motors['head'].append(m)

    reachy = RobotSubPart(robot, motors['reachy'])
    leachy = RobotSubPart(robot, motors['leachy'])
    head = RobotSubPart(robot, motors['head'])

    return robot, reachy, leachy, head
