# This dictionary will hold all NPC stat blocks.
default npc_roster = {}

# This label should be called once at the beginning of the game to populate the roster.
label initialize_npcs:
    # --- NPC ROSTER INITIALIZATION ---
    $ npc_roster["zev"] = CharacterStats(name="Zev", hp=12, ac=12, str=8, dex=14, con=10, intl=12, wis=14, cha=10)
    $ npc_roster["sevika"] = CharacterStats(name="Sevika", hp=45, ac=16, str=18, dex=14, con=16, intl=12, wis=12, cha=14)
    $ npc_roster["zaunite_thug_template"] = CharacterStats(name="Zaunite Thug", hp=15, ac=13, str=14, dex=12, con=12, intl=8, wis=8, cha=8)
    return
