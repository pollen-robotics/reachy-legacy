from numpy import sum
from functools import partial


from poppy.creatures import AbstractPoppyCreature


class Reachy(AbstractPoppyCreature):
    @classmethod
    def setup(cls, robot):
        robot._primitive_manager._filter = partial(sum, axis=0)
