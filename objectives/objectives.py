import worlds.ff6wc.WorldsCollide.args as args

from worlds.ff6wc.WorldsCollide.objectives.results import results
from worlds.ff6wc.WorldsCollide.objectives.conditions import conditions
from worlds.ff6wc.WorldsCollide.objectives.objective import Objective

from worlds.ff6wc.WorldsCollide.objectives.result_dict import ResultDict

class Objectives:
    results = ResultDict()

    def __init__(self):
        self.objectives = []
        self.suplex_train_condition_exists = False
        for index in range(len(args.objectives)):
            objective = Objective(index)
            self.objectives.append(objective)

            if objective.result.NAME in Objectives.results:
                Objectives.results[objective.result.NAME].append(objective)
            else:
                Objectives.results[objective.result.NAME] = [objective]

            if objective.has_suplex_train_condition:
                self.suplex_train_condition_exists = True

    def __len__(self):
        return len(self.objectives)

    def __getitem__(self, index):
        return self.objectives[index]
