from worlds.ff6wc.WorldsCollide.bug_fixes.evade import Evade
from worlds.ff6wc.WorldsCollide.bug_fixes.sketch import Sketch
from worlds.ff6wc.WorldsCollide.bug_fixes.vanish_doom import VanishDoom
from worlds.ff6wc.WorldsCollide.bug_fixes.jump import Jump
from worlds.ff6wc.WorldsCollide.bug_fixes.retort import Retort
from worlds.ff6wc.WorldsCollide.bug_fixes.enemy_damage_counter import EnemyDamageCounter
from worlds.ff6wc.WorldsCollide.bug_fixes.capture import Capture

__all__ = ["BugFixes"]
class BugFixes:
    def __init__(self):
        self.evade = Evade()
        self.sketch = Sketch()
        self.vanish_doom = VanishDoom()
        self.jump = Jump()
        self.retort = Retort()
        self.enemy_damage_counter = EnemyDamageCounter()
        self.capture = Capture()
