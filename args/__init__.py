from worlds.ff6wc.WorldsCollide.args.arguments import Arguments
ap_data = None

def main(ap_args):
    arguments = Arguments(ap_args)

    import sys
    module = sys.modules[__name__]
    for name, value in arguments.__dict__.items():
        setattr(module, name, value)
    from worlds.ff6wc.WorldsCollide.args.log import log
