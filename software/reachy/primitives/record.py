import csv
import numpy as np

from pypot.primitive import LoopPrimitive


class MoveRecorder(LoopPrimitive):
    def __init__(self, robot, motors):
        LoopPrimitive.__init__(self, robot, 50)
        self.motors = motors

    def setup(self):
        self.data = []

    def update(self):
        pos = {m.name: m.present_position for m in self.motors}
        self.data.append(pos)

    def save(self, filename):
        with open(filename, 'w') as f:
            w = csv.DictWriter(f, self.data[0].keys())
            w.writeheader()
            w.writerows(self.data)


class MovePlayer(LoopPrimitive):
    def __init__(self, robot, move_file):
        LoopPrimitive.__init__(self, robot, 50)

        with open(move_file) as f:
            self.reader = csv.DictReader(f)
            self.data = [row for row in self.reader]
            self.i = 0

    def setup(self):
        self.i = 0

    def update(self):
        try:
            pos = self.data[self.i]
            for m, p in pos.items():
                getattr(self.robot, m).goal_position = float(p)
            self.i += 1
        except IndexError:
            self.stop()
