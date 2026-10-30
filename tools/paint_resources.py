"""
Paint the portraits and room pictures in story/resources with Gemini's image model.

Needs GEMINI_API_KEY (or .env). The style lives in story/tintype.py, shared with the game,
which paints the Stranger's portrait when Gemma invents them.

    python tools/paint_resources.py            # paint missing images
    python tools/paint_resources.py lars_öberg  # repaint one
"""
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
RESOURCES = ROOT / "story" / "resources"
sys.path.insert(0, str(ROOT / "story"))

from tintype import paint_portrait, paint_room  # noqa: E402

PORTRAITS = {
    "brita_lindqvist": "The ghost of a pale, translucent young Swedish woman of 29 in a faded blue folk costume and a white linen headscarf, hollow cheeks from fever, sorrowful eyes.",
    "gustaf_nilsson": "A hulking grey-skinned dead man of 41 in a leather brewer's apron stiff with old blood, one side of his skull caved in, frost clinging to his beard.",
    "sigrid_ahlgren": "A tall vampire lady in an immaculate black silk mourning dress decades out of fashion, porcelain white skin, dark lips, eyes catching candle light like a cat's.",
    "anders_holm": "A gaunt, unshaven trapper of 34 in a torn wolfskin coat, coarse grey hair on the backs of his hands, eyes a little too yellow.",
    "näcken": "Näcken, the beautiful water spirit of Swedish folklore: a young man with bare shoulders standing chest-deep in black creek water, water lilies tangled in his long hair, playing a dark fiddle.",
    "lars_öberg": "A stooped, frightened old lamplighter of 67 in a patched wool coat and a flat cap, holding a long lantern pole with a hook.",
    "reaper": "The Grim Reaper: a figure in black hooded robes with only nothingness where the face should be, holding a large ominous scythe.",
}
ROOMS = {
    "the_heart_of_swede_hollow": "A muddy street winding between crooked wooden houses and log shanties in a steep ravine, shuttered windows, a single street lantern.",
    "the_old_swedish_cemetery": "A small overgrown cemetery on the edge of the ravine, leaning wooden crosses and weathered stones with Swedish names, wilted flowers.",
    "a_crumbling_cellar_entrance": "An old wooden cellar door hanging ajar in a hillside, stone steps leading down into the dark earth.",
    "a_dark,_damp_root_cellar": "A long-abandoned root cellar beneath an old house, rotting shelves with jars, roots through the earthen walls, a lantern glow.",
    "the_muddy_bank_of_phalen_creek": "The muddy bank of a sluggish dark creek at the bottom of the ravine, reeds and fog over the water, the bluff above.",
}


def api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        for line in (ROOT / ".env").read_text().splitlines():
            if line.startswith("GEMINI_API_KEY="):
                key = line.split("=", 1)[1].strip().strip("'\"")
    if not key:
        sys.exit("GEMINI_API_KEY not set")
    return key


def main(only: list) -> None:
    jobs = [(name, subject, paint_portrait) for name, subject in PORTRAITS.items()]
    jobs += [(name, subject, paint_room) for name, subject in ROOMS.items()]
    for name, subject, painter in jobs:
        path = RESOURCES / f"{name}.jpg"
        if (only and name not in only) or (not only and path.exists()):
            continue
        print(f"painting {path.name}")
        painter(subject, api_key()).save(path, quality=85)


if __name__ == "__main__":
    main(sys.argv[1:])
