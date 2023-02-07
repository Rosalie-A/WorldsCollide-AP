from worlds.ff6wc.WorldsCollide.objectives.conditions._objective_condition import *
from worlds.ff6wc.WorldsCollide.constants.objectives.condition_bits import check_bit

class Condition(ObjectiveCondition):
    NAME = "Check"
    def __init__(self, check):
        self.check = check
        super().__init__(ConditionType.EventBit, check_bit[self.check].bit)

    def __str__(self):
        return super().__str__(self.check)
