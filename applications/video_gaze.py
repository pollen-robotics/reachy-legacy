import zmq

CAM_RES = (1280, 720)

import time
import numpy

from reachy import Leachy
leachy = Leachy()

screen_size = (520, 320)  # in mm

joints = {  # in degrees
    'pyramide_rouge':  [-28.33, 20.1, 36.97, -64.22, -34.16, 10.7, -20.0],
    'prisme_jaune': [-49.69, 18.31, 17.27, -35.47, -53.52, -0.15, -7.89],
    'hexa_jaune':  [4.7, -2.35, 41.19, -98.51, -7.18, 22.43, -19.21],
    'pyramide_vert': [-21.9, 2.2, 12.79, -71.08, -45.6, 13.34, -20.38] ,
    'cube_rouge': [-33.43, -6.6, 15.6, -55.43, -61.14, -11.58, -6.6],
    'boule_jaune':  [3.85, -0.68, 24.84, -85.67, -56.16, -23.02, -20.67],
    'cylindre_bleu': [-44.07, 6.3, -33.36, -44.18, -22.43, -3.08, -21.26],
    'chapeau_vert':[4.8, 15.9, -15.69, -94.55, -34.75, -1.32, -17.74] ,
    'rest':  [16.6, 13.6, 17.1, -101.93, -19.5, -0.15, -16.28],
    'center': [-19.2, 9.3, 2.24, -93.23, -28.3, 14.52, -7.48],
}

inter = {
    'pyramide_rouge': True,
    'prisme_jaune': True,
    'hexa_jaune': False,
    'pyramide_vert': True,
    'cube_rouge': True,
    'boule_jaune': False,
    'cylindre_bleu': True,
    'chapeau_vert': False,
}

pos_2d = {  # in mm (origin top left)
    'pyramide_rouge': (35, 145),
    'prisme_jaune': (145, 65),
    'hexa_jaune': (110, 260),
    'pyramide_vert': (270, 160),
    'cube_rouge': (350, 70),
    'boule_jaune': (300, 250),
    'cylindre_bleu': (470, 135),
    'chapeau_vert': (465, 275),
}

time_traj = {
    'pyramide_rouge': 1,
    'prisme_jaune': 1,
    'hexa_jaune': 0.75,
    'pyramide_vert': 1,
    'cube_rouge': 1,
    'boule_jaune': 0.75,
    'cylindre_bleu': 1,
    'chapeau_vert': 0.75,
}

def find_nearest_object(x, y):
    dist = {
        corner: (xc - x) ** 2 + (yc - y) ** 2
        for (corner, (xc, yc)) in pos_2d.items()
    }
    return min(dist, key=dist.get)


def goto_object(obj, t, wait=True):
    print('Goto obj:', obj)
    q = joints[obj]

    for m, p in zip(leachy.motors, q):
        m.goto_position(p, t, control='linear')
    if wait:
        time.sleep(t)


def goto_2d(x2, y2):
    x2 = min(max(x2, 0), 1)
    y2 = min(max(y2, 0), 1)

    x2 *= screen_size[0]
    y2 *= screen_size[1]

    obj = find_nearest_object(x2, y2)
    goto(obj)


def goto_rest(t):
    for m, p in zip(leachy.motors, joints['center']):
        m.goto_position(p, t, control='linear')
    time.sleep(t)


def goto(obj):
    t = time_traj[obj]

    if inter[obj]:
        goto_object('center', t, wait=True)
        #time.sleep(0.75 * t)
    goto_object(obj, t)
    time.sleep(t)
    if inter[obj]:
        goto_object('center', t, wait=True)
        #time.sleep(0.75 * t)

    goto_object('rest', t)



import myo


class Listener(myo.DeviceListener):
    def on_connect(self, device, timestamp, version):
        print('Connected!')

        device.set_stream_emg(myo.StreamEmg.enabled)

        for _ in range(3):
            device.vibrate('short')
            time.sleep(0.5)

    def on_emg_data(self, device, timestamp, emg):
        self.emg = abs(numpy.array(emg))


from threading import Thread


if __name__ == '__main__':
    import sys

    import cv2

    for m in leachy.motors:
        m.compliant = False
        m.moving_speed = 0

    #goto_rest(2)

    #myo.init('../../myo-sdk-win-0.9.0/bin')

    #listener = Listener()
    #listener.emg = numpy.array([numpy.nan])

    #hub = myo.Hub()
    #hub.run(50, listener)

    from gazepoint import GazePoint
    tracker = GazePoint()

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_RES[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_RES[1])

    cv2.namedWindow('cam', cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty('cam', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)


    while True:
        ret, frame = cap.read()

        x, y = tracker.gaze_position
        cv2.circle(frame, (round(x * CAM_RES[0]), round(y * CAM_RES[1])), 10, (0, 0, 225), -1)

        cv2.imshow('cam', frame)
        key = cv2.waitKey(50)

        if key == 13: # Enter
            Thread(target=lambda: goto_2d(x, y)).start()

        if key in (27, ord('q')): # Esc or 'q'
            break

    tracker.stop()
    hub.shutdown()
