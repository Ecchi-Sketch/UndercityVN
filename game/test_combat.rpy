# Test label for combat system
label test_combat:
    "Testing the combat encounter window..."
    
    # Initialize NPCs if not already done
    if not npc_roster:
        call initialize_npcs
    
    # Create Sevika if she doesn't exist yet
    if "sevika" not in npc_roster:
        $ sevika_stats = CharacterStats(
            name=default_npc_stats["sevika"]["name"],
            hp=default_npc_stats["sevika"]["hp"],
            ac=default_npc_stats["sevika"]["ac"],
            strength=default_npc_stats["sevika"]["str"],
            dexterity=default_npc_stats["sevika"]["dex"],
            constitution=default_npc_stats["sevika"]["con"],
            intelligence=default_npc_stats["sevika"]["intl"],
            wisdom=default_npc_stats["sevika"]["wis"],
            charisma=default_npc_stats["sevika"]["cha"],
            atk_bonus=4
        )
        $ npc_roster["sevika"] = sevika_stats
        
        # Give Sevika her signature weapon
        $ sevika_stats.inventory["sevikas_puncher"] = 1
        $ sevika_stats.equip_item("sevikas_puncher")
    
    # Set up the combat interface data
    $ combat_participants = [player_stats, npc_roster["sevika"]]
    $ current_turn_index = 0
    $ combat_round = 1
    $ combat_log = ["Combat against Sevika begins!", "Sevika readies her blade arm and smirks."]
    $ pending_roll = None
    $ selected_action = None
    $ selected_target = None
    
    "You find yourself facing Sevika, one of the most dangerous enforcers in the Undercity."
    "Her mechanical arm gleams menacingly in the dim light as she prepares for battle."
    
    "Combat interface loading..."
    
    # Call the combat encounter screen
    call screen combat_encounter
    
    "Combat test complete!"
    return
