conditions = {}
def __init__():
    import os, importlib
    for module_file in os.listdir(os.path.dirname(__file__)):
        pyc = False
        if module_file[0] == '_':
            continue
        elif module_file[-3:] == "pyc":
            pyc = True
        elif module_file[-3:] != ".py":
            continue
        if pyc:
            module_name = module_file[:-4]
        else:
            module_name = module_file[:-3]
        module = importlib.import_module("." + module_name, "worlds.ff6wc.WorldsCollide.objectives.conditions")

        conditions[module.Condition.NAME] = module.Condition
__init__()
