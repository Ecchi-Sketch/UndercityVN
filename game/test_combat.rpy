# Test label for the new combat system

label test_combat:
    "Initializing combat test environment..."

    # Initialize the player character's stats and loadout.
    # This label is now in NPCRoster.rpy, ensuring correct load order.
    call initialize_player_character

    # Initialize the NPC roster.
    if not npc_roster:
        "No NPCs found, initializing roster..."
        call initialize_npcs

    "You find yourself facing Sevika, one of the most dangerous enforcers in the Undercity."
    "Her mechanical arm gleams menacingly in the dim light as she prepares for battle."

    # --- COMBAT START ---
    # We gather the opponents we want to fight from the now-initialized roster.
    $ opponents_for_this_fight = [npc_roster["sevika"]]

    # We call the start_combat label, which handles creating the controller
    # and showing the combat screen. It correctly uses the 'player_stats' object.
    call start_combat(opponents_for_this_fight)
    # ----------------------

    "Combat test complete! The combat screen has returned."
    "You can check the logs or console for details of the fight."

    return
