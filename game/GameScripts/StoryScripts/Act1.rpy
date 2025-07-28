label Act1_Scene1_intro:

    show screen player_hud

    "Act1 Scene 1 Test narration"
    player "My name is [player_name]"

    $ player_stats.add_item("iron_knuckles", 1)
    "You find a pair of heavy Iron Knuckles on the ground and pocket them."
    $ player_stats.add_item("makeshift_shiv", 1)
    "You find a makeshift shiv on the ground and pocket it."
    $ player_stats.add_item("reinforced_vest", 1)
    "You find a reinforced vest on the ground and put it on."
    $ player_stats.add_item("old_sewer_key", 1)
    "You find an old sewer key on the ground and pocket it."
    $ player_stats.add_item("healing_draught", 5)
    "You find a healing draught on the ground and pocket it."
    $ player_stats.add_item("scrap_metal", 5)
    "You find scrap metal on the ground and pocket it."

label Act1_Scene2_Welcome:

    "Act 1 Scene 2 Test narration"
    player "My Stats are: str:[player_stats.strength], dex:[player_stats.dexterity]"

    return