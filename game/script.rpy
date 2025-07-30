# The game starts here. The 'label start:' is the default entry point for a new game.
label start:
    # We now call the character creation screen first.
    call screen character_creation
    # The screen above will JUMP to game_start, so code here is unreachable.

# This label starts the actual game narrative after creation is complete.
label game_start:
    # Initialize the item database, NPC roster, skills, and recipes.
    # IMPORTANT: Items must be initialized before NPCs so they can equip items!
    call initialize_items
    call initialize_skills
    call initialize_recipes
    call initialize_npcs

    menu:
        "Act 1":
            jump Act1_Scene1_intro
        "Choice 2 Description":
            jump Choice_2_Result
        "Choice 3 Description":
            jump Choice_3_Result
    
    return

