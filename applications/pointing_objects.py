import time

from reachy import Leachy


leachy = Leachy()

screen_size = (520, 320)  # in mm

joints = {  # in degrees
    'cat': [-37.47, 24.37, 22.9, -110.55, 9.24, 45.31, -15.1],
    'tomato': [-34.84, 13.21, 11.47, -125.93, 8.65, 54.69, -15.98],
    'chocolatine': [-27.80, -0.86, -2.51, -128.48, 8.94, 30.26, -15.98],
    'kangoo': [-13.65, 16.11, 29.58, -106.77, 12.76, 24.78, -18.62],
    'cow': [-11.89, 7.58, 18.77, -121.63, 11.88, 36.22, -20.97],
    'snes': [-8.37, 1.3, -2.95, -130.24, 10.12, 37.39, -20.38],
    'center': [-19.63, 12.15, 17.01, -127.6, 14.52, 50.29, -21.55],
    'outside_fov': [9.12, 6.79, 21.67, -123.47, 15.4, 23.02, -22.14],
}

pos_2d = {  # in mm (origin top left)
    'cat': (60, 50),
    'tomato': (240, 70),
    'chocolatine': (430, 80),
    'kangoo': (50, 240),
    'cow': (230, 240),
    'snes': (430, 260),
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
