#// ------------------------------------------------------------------------------------------------
#// Character Sheet and HUD
#// ------------------------------------------------------------------------------------------------
#// The Active Effects panel is now dynamic. It will automatically display any effect
#// found in an item's 'effects' dictionary, making the system more robust.
#// ------------------------------------------------------------------------------------------------

# Screen for the button that toggles the character sheet.
screen player_hud():
    zorder 100
    textbutton "Character" action ToggleScreen("player_stats_screen"):
        xalign 0.01
        yalign 0.01

# Screen for displaying player stats, inventory, and equipment.
screen player_stats_screen():
    modal True

    frame:
        xalign 0.5
        yalign 0.5
        xsize 2560
        yminimum 600
        padding (30, 30)

        vbox:
            xalign 0.5
            spacing 15

            # --- HEADER ---
            hbox:
                null width 50
                text "Character Sheet" size 30 xalign 0.5
                textbutton "X" action Hide("player_stats_screen"):
                    xalign 1.0
                    yalign 0.0

            add Solid("#404040", xfill=True, ysize=1)

            if player_stats:
                # --- MAIN CONTENT (STATS AND ITEMS) ---
                hbox:
                    spacing 30

                    # --- LEFT COLUMN (STATS) ---
                    vbox:
                        xsize 750
                        spacing 10
                        text "Attributes" size 22
                        null height 5

                        hbox:
                            text "HP:" xsize 150
                            text "[player_stats.hp] / [player_stats.max_hp]"
                        hbox:
                            text "AC:" xsize 150
                            text "[player_stats.ac]"

                        null height 15

                        hbox:
                            text "Strength:" xsize 150
                            text "[player_stats.strength]"
                        hbox:
                            text "Dexterity:" xsize 150
                            text "[player_stats.dexterity]"
                        hbox:
                            text "Constitution:" xsize 150
                            text "[player_stats.constitution]"
                        hbox:
                            text "Intelligence:" xsize 150
                            text "[player_stats.intelligence]"
                        hbox:
                            text "Wisdom:" xsize 150
                            text "[player_stats.wisdom]"
                        hbox:
                            text "Charisma:" xsize 150
                            text "[player_stats.charisma]"

                    # --- MIDDLE COLUMN (EQUIPMENT & INVENTORY) ---
                    vbox:
                        xsize 750
                        spacing 20

                        # --- EQUIPPED ITEMS ---
                        vbox:
                            spacing 8
                            text "Equipped Items" size 22
                            null height 5

                            if player_stats.equipped_items:
                                for item in player_stats.equipped_items:
                                    hbox:
                                        text item.name style "equipped_item_text"
                                        textbutton "Unequip" text_style "inventory_button_text" action Function(player_stats.unequip, item_to_unequip=item) xalign 1.0
                            else:
                                text "Nothing equipped." style "description_text"


                        # --- INVENTORY ---
                        vbox:
                            spacing 8
                            text "Inventory" size 22
                            null height 5

                            viewport:
                                xsize 750
                                ysize 300
                                scrollbars "vertical"
                                mousewheel True
                                draggable True

                                vbox:
                                    spacing 5
                                    if player_stats.inventory:
                                        for item in player_stats.inventory:
                                            hbox:
                                                text item.name
                                                null 
                                                textbutton "Equip" text_style "inventory_button_text" action Function(player_stats.equip, item_to_equip=item) xalign 1.0  
                                    else:
                                        text "Your bag is empty."
                    
                    # --- RIGHT COLUMN (ACTIVE EFFECTS) ---
                    vbox:
                        xsize 750
                        spacing 10
                        text "Active Effects" size 22
                        null height 5
                        
                        # --- Equipped Item Effects ---
                        if player_stats.equipped_items:
                            for item in player_stats.equipped_items:
                                # This python block now dynamically formats any effect in the item's dictionary.
                                python:
                                    effects_str = []
                                    # Loop through all key-value pairs in the item's effects.
                                    for key, value in item.effects.items():
                                        # Default format for unknown effects.
                                        formatted_effect = "{}: {}".format(key.replace('_', ' ').capitalize(), value)

                                        # Custom formatting for known effect types to make them look nice.
                                        if key == "ac_bonus":
                                            formatted_effect = "+{} AC".format(value)
                                        elif key == "max_hp_percent_bonus":
                                            formatted_effect = "+{}% Max HP".format(int(value * 100))
                                        elif key == "damage":
                                            formatted_effect = "Damage: {}".format(value)
                                        elif "_bonus" in key:
                                            # Handles any stat bonus like "strength_bonus", "dexterity_bonus", etc.
                                            stat_name = key.replace('_bonus', '').upper()
                                            formatted_effect = "+{} {}".format(value, stat_name)
                                        
                                        effects_str.append(formatted_effect)

                                    # Join all formatted effects with a comma.
                                    display_effects = ", ".join(effects_str)

                                text "Equipped - [item.name]: [display_effects]" style "description_text"

                        # --- Passive Effects ---
                        # You can add logic here later for passive abilities
                        text "Passive - None"


            else:
                text "Character data not yet available. Please complete character creation." xalign 0.5
