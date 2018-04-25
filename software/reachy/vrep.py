from reachy import Reachy, Leachy


def multi_robot_from_vrep(scene, robots):
    if len(robots) < 1:
        raise ValueError('Empty list of tracked robots provided!')

    if len(robots) == 1:
        return from_vrep(scene, robots[0])

    robots = list(robots)

    first = from_vrep(scene, robots.pop(0))
    vrep_io = first._controllers[0].io

    robots = [
        from_vrep(scene='keep-existing', robot=r, shared_vrep_io=vrep_io)
        for r in robots
    ]
    return [first] + robots


def extract_robot(robot):
    poss = ('reachy', 'leachy')
    for p in poss:
        if robot.startswith(p):
            id = robot[len(p):]
            id = None if id == '' else int(id)
            return p, id

    raise ValueError('robot must be in {}!'.format(poss))


def from_vrep(scene, robot, **extra):
    robot, id = extract_robot(robot)
    extra['id'] = id

    if robot == 'reachy':
        return Reachy(simulator='vrep', scene=scene, **extra)
    if robot == 'leachy':
        return Leachy(simulator='vrep', scene=scene, **extra)

    raise ValueError('Robot must either "reachy" or "leachy"!')
