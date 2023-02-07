def __init__():
    from worlds.ff6wc.WorldsCollide.data.fonts.widths import Widths
    widths = Widths()

    import sys, inspect
    module = sys.modules[__name__]
    module.widths = widths
__init__()
