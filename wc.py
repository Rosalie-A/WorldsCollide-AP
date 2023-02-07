import worlds.ff6wc.WorldsCollide.args as args
def main(ap_args):

    args.main(ap_args)
    import worlds.ff6wc.WorldsCollide.log

    from worlds.ff6wc.WorldsCollide.memory.memory import Memory
    memory = Memory()

    from worlds.ff6wc.WorldsCollide.data.data import Data
    data = Data(memory.rom, args)

    from worlds.ff6wc.WorldsCollide.event.events import Events
    events = Events(memory.rom, args, data)

    from worlds.ff6wc.WorldsCollide.menus.menus import Menus
    menus = Menus(data.characters, data.dances, data.rages, data.enemies)

    from worlds.ff6wc.WorldsCollide.battle import Battle
    battle = Battle()

    from worlds.ff6wc.WorldsCollide.settings import Settings
    settings = Settings()

    from worlds.ff6wc.WorldsCollide.bug_fixes import BugFixes
    bug_fixes = BugFixes()

    data.write()
    memory.write()

if __name__ == '__main__':
    main()
