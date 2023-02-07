def get_palettes():
    from worlds.ff6wc.WorldsCollide.graphics.palettes.palettes import id_palette
    from worlds.ff6wc.WorldsCollide.api.get_palette_bytes import get_palette_bytes

    palettes = [{
        'id': palette_id,
        'key': key,
    } for ((palette_id, key)) in id_palette.items()]

    return palettes

def get_palettes_with_colors():
    from worlds.ff6wc.WorldsCollide.graphics.palettes.palettes import id_palette
    from worlds.ff6wc.WorldsCollide.api.get_palette_bytes import get_palette_bytes

    palettes = [{
        'id': palette_id,
        'key': key,
        'palette': get_palette_bytes(palette_id)
    } for ((palette_id, key)) in id_palette.items()]

    return palettes

if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

    import json
    print(json.dumps(get_palettes()))
