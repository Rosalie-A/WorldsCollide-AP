import worlds.ff6wc.WorldsCollide.battle.formation_flags
from worlds.ff6wc.WorldsCollide.battle.multipliers import Multipliers
import worlds.ff6wc.WorldsCollide.battle.load_enemy_level
import worlds.ff6wc.WorldsCollide.battle.no_exp_party_divide
import worlds.ff6wc.WorldsCollide.battle.suplex_train_check
import worlds.ff6wc.WorldsCollide.battle.auto_status
import worlds.ff6wc.WorldsCollide.battle.end_checks
import worlds.ff6wc.WorldsCollide.battle.magitek_upgrade
from worlds.ff6wc.WorldsCollide.battle.animations import Animations

__all__ = ["Battle"]
class Battle:
    def __init__(self):
        self.multipliers = Multipliers()
        self.animations = Animations()
