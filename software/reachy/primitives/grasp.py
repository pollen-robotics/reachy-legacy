import time

from pypot.primitive import Primitive


class Grasp(Primitive):
    def setup(self):
        self.robot.finger_grip.compliant = False

    def run(self):
        self.robot.finger_grip.moving_speed = 200
        time.sleep(2)
        self.robot.finger_grip.moving_speed = 0

    def teardown(self):
        self.robot.finger_grip.compliant = True


class Release(Primitive):
    def setup(self):
        self.robot.finger_grip.compliant = False

    def run(self):
        self.robot.finger_grip.moving_speed = -100
        time.sleep(2)
        self.robot.finger_grip.moving_speed = 0

    def teardown(self):
        self.robot.finger_grip.compliant = False
