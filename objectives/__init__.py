import sys
module = sys.modules[__name__]

from worlds.ff6wc.WorldsCollide.objectives.objectives import Objectives
sys.modules[__name__] = Objectives()
