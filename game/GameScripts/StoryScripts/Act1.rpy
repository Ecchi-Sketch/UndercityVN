label Act1_Scene1_intro:

    show screen player_hud

    "Act1 Scene 1 Test narration"
    player "My name is [player_name]"
    $ player_stats.inventory.append(item_database["iron_knuckles"])
    "You find a pair of heavy Iron Knuckles on the ground and pocket them."
    $ player_stats.inventory.append(item_database["makeshift_shiv"])
    "You find a makeshift shiv on the ground and pocket it."
    $ player_stats.inventory.append(item_database["reinforced_vest"])
    "You find a reinforced vest on the ground and put it on."



label Act1_Scene2_Welcome:

    "Act 1 Scene 2 Test narration"
    player "My Stats are: str:[player_stats.strength], dex:[player_stats.dexterity]"

    return