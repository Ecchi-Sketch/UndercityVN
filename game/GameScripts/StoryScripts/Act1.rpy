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
    $ player_stats.add_item("leather", 3)
    "You find some leather scraps and pocket them."
    $ player_stats.add_item("cloth", 3)
    "You find some cloth scraps and pocket them."
    $ player_stats.add_item("herb", 4)
    "You find some herbs growing between the cobblestones and collect them."
    $ player_stats.learn_skill("new_kid_in_town")
    "You acquired the skill: New Kid in Town!"
    $ player_stats.learn_skill("test_skill")
    "You acquired the skill: Test Skill!"
    $ player_stats.gain_xp(base_amount=0, skill_amount=20000)
    "You've been granted an addtional 20000 skill XP!"

label Act1_Scene2_Welcome:

    "Act 1 Scene 2 Test narration"
    player "My Stats are: str:[player_stats.strength], dex:[player_stats.dexterity]"

    return