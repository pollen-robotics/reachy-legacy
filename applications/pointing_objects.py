import time

from reachy import Leachy


leachy = Leachy()

screen_size = (520, 320)  # in mm

joints = {  # in degrees
    'cat': [-40.02, 10.04, 27.56, -80.75, -3.67, -12.2, -12.76],
    'tomato': [-34.48, 11.45, 9.1, -91.38, -1.32, 0.44, -12.46],
    'chocolatine': [-34.66, -6.0, -0.4, -94.99, -1.32, 3.67, -12.46],
    'wall_e': [-35.1, -12.37, -15.16, -86.29, -1.32, -6.89, -12.46],
    'kangoo': [-24.64, 12.15, 24.4, -70.55, -0.44, -17.74, -10.12],
    'cow': [-21.12, 2.57, 12.18, -78.29, -0.44, -18.62, -10.12],
    'snes': [-19.8, -4.81, -4.18, -81.45, -0.44, -19.21, -10.12],
    'coffee': [-23.23, -11.32, -18.77, -74.42, -0.44, -24.19, -10.12],
    'center': [-14.26, -0.07, 2.07, -87.34, -0.15, -17.16, -7.18],
    'outside_fov': [9.12, 6.79, 21.67, -123.47, 15.4, 23.02, -22.14],
}

pos_2d = {  # in mm (origin top left)
    'cat': (40, 70),
    'tomato': (205, 70),
    'chocolatine': (370, 70),
    'wall_e': (525, 70),
    'kangoo': (50, 230),
    'cow': (210, 220),
    'snes': (370, 230),
    'coffee': (520, 230),
}


def find_nearest_object(x, y):
    dist = {
        corner: (xc - x) ** 2 + (yc - y) ** 2
        for (corner, (xc, yc)) in pos_2d.items()
    }
    return min(dist, key=dist.get)


def goto_object(obj, t):
    print('Goto obj:', obj)
    q = joints[obj]

    for m, p in zip(leachy.motors, q):
        m.goto_position(p, t, control='minjerk')
    time.sleep(t + 0.5)


def goto_2d(x2, y2, t):
    x2 = min(max(x2, 0), 1)
    y2 = min(max(y2, 0), 1)

    x2 *= screen_size[0]
    y2 *= screen_size[1]

    obj = find_nearest_object(x2, y2)
    goto_object(obj, t)


def goto_rest(t):
    for m, p in zip(leachy.motors, joints['center']):
        m.goto_position(p, t, control='minjerk')
    time.sleep(t)


if __name__ == '__main__':
    """ Example: python pointing_objects.py snes cow cat """
    import sys

    for m in leachy.motors:
        m.compliant = False
        m.moving_speed = 0

    goto_rest(2)

    for obj in sys.argv[1:]:
        goto_object(obj, 1)

    goto_rest(2)
