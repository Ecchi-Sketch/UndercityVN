#// ------------------------------------------------------------------------------------------------
#// Character Sheet and HUD
#// ------------------------------------------------------------------------------------------------
#// The inventory is now a tabbed interface with support for stackable items.
#// ------------------------------------------------------------------------------------------------

# Screen for the button that toggles the character sheet.
screen player_hud():
    zorder 100
    textbutton "Character" action ToggleScreen("player_stats_screen"):
        xalign 0.01
        yalign 0.01

# Screen for displaying player stats, inventory, and equipment.
screen player_stats_screen():
    # This variable will keep track of which inventory tab is currently active.
    default inventory_tab = "equippable"
    modal True

    frame:
        xalign 0.5
        yalign 0.5
        xsize 2560
        yminimum 600
        ymaximum 1280
        padding (30, 30)

        vbox:
            xalign 0.5
            spacing 15

            # --- HEADER ---
            hbox:
                null width 5
                textbutton "X" text_style "red_white_highlight_text" action Hide("player_stats_screen"):
                    xalign -1.0
                    yalign 0.0
                text "Character Info Screen - [player_name]" size 60 xalign 1.0

            add Solid("#404040", xfill=True, ysize=1)

            if player_stats:
                # --- MAIN CONTENT (STATS AND ITEMS) ---
                hbox:
                    spacing 30

                    # --- LEFT COLUMN (STATS) ---
                    vbox:
                        xsize 450
                        spacing 10
                        text "Attributes" size 30
                        null height 5

                        hbox:
                            text "HP:" xsize 150
                            text "[player_stats.hp] / [player_stats.max_hp]"
                        hbox:
                            text "AC:" xsize 150
                            text "[player_stats.ac]"

                        null height 15

                        hbox:
                            text "Strength:" xsize 150 style "item_text"
                            text "[player_stats.strength]" style "item_text"
                        hbox:
                            text "Dexterity:" xsize 150 style "item_text"
                            text "[player_stats.dexterity]" style "item_text"
                        hbox:
                            text "Constitution:" xsize 150 style "item_text"
                            text "[player_stats.constitution]" style "item_text"
                        hbox:
                            text "Intelligence:" xsize 150 style "item_text"
                            text "[player_stats.intelligence]" style "item_text"
                        hbox:
                            text "Wisdom:" xsize 150 style "item_text"
                            text "[player_stats.wisdom]" style "item_text"
                        hbox:
                            text "Charisma:" xsize 150 style "item_text"
                            text "[player_stats.charisma]" style "item_text"

                    add Solid("#404040", yfill=True, xsize=1)

                    # --- MIDDLE COLUMN (EQUIPMENT & INVENTORY) ---
                    vbox:
                        xsize 1000
                        spacing 20

                        # --- EQUIPPED ITEMS ---
                        vbox:
                            spacing 8
                            text "Equipped Items" size 30
                            null height 5

                            if player_stats.equipped_items:
                                for item in player_stats.equipped_items:
                                    hbox:
                                        text item.name
                                        null
                                        textbutton "Unequip" text_style "inventory_button_text" action Function(player_stats.unequip, item_to_unequip=item)
                            else:
                                text "Nothing equipped."

                        add Solid("#404040", xfill=True, ysize=1)


                        # --- INVENTORY (NOW WITH TABS) ---
                        vbox:
                            spacing 8
                            text "Inventory" size 30
                            
                            # --- Tab Buttons ---
                            hbox:
                                spacing 10
                                textbutton "Equippable" action SetScreenVariable("inventory_tab", "equippable") text_style "item_tab_text"
                                textbutton "Consumables" action SetScreenVariable("inventory_tab", "consumable") text_style "item_tab_text"
                                textbutton "Plot" action SetScreenVariable("inventory_tab", "plot") text_style "item_tab_text"
                                textbutton "Misc" action SetScreenVariable("inventory_tab", "misc") text_style "item_tab_text"

                            # --- Tabbed Viewport ---
                            viewport:
                                xsize 1000
                                ysize 750
                                scrollbars "vertical"
                                mousewheel True
                                draggable True

                                vbox:
                                    spacing 5
                                    
                                    # This python block checks if there are any items of the currently selected category to display.
                                    python:
                                        category_has_items = False
                                        for item_id in player_stats.inventory:
                                            if item_database[item_id].category == inventory_tab:
                                                category_has_items = True
                                                break
                                    
                                    # Loop through the inventory dictionary (item_id: count)
                                    for item_id, count in player_stats.inventory.items():
                                        # Get the full item object from the database using its ID
                                        python:
                                            item = item_database[item_id]

                                        # Only display items that match the currently selected tab
                                        if item.category == inventory_tab:
                                            hbox:
                                                # Display name and stack count
                                                text "{} (x{})".format(item.name, count) style "item_text"
                                                null
                                                
                                                # Show the correct button based on the category
                                                if item.category == "equippable":
                                                    textbutton "Equip" text_style "inventory_button_text" action Function(player_stats.equip, item_id=item_id)
                                                elif item.category == "consumable":
                                                    textbutton "Use" text_style "inventory_button_text" action Function(player_stats.use_consumable, item_id=item_id)
                                    
                                    if not category_has_items:
                                        text "No items of this type." style "item_text"
                    add Solid("#404040", yfill=True, xsize=1)        


                    # --- RIGHT COLUMN (ACTIVE EFFECTS) ---
                    vbox:
                        xsize 750
                        spacing 10
                        text "Active Effects" style "item_text"
                        null height 5
                        
                        if player_stats.equipped_items:
                            for item in player_stats.equipped_items:
                                python:
                                    effects_str = []
                                    for key, value in item.effects.items():
                                        formatted_effect = "{}: {}".format(key.replace('_', ' ').capitalize(), value)
                                        if key == "ac_bonus":
                                            formatted_effect = "+{} AC".format(value)
                                        elif key == "max_hp_percent_bonus":
                                            formatted_effect = "+{}% Max HP".format(int(value * 100))
                                        elif key == "damage":
                                            formatted_effect = "Damage: {}".format(value)
                                        elif "_bonus" in key:
                                            stat_name = key.replace('_bonus', '').upper()
                                            formatted_effect = "+{} {}".format(value, stat_name)
                                        effects_str.append(formatted_effect)
                                    display_effects = ", ".join(effects_str)

                                text "Equipped - [item.name]: [display_effects]"  style "description_text"

                        text "Passive Effects" style "item_text"


            else:
                text "Character data not yet available. Please complete character creation." xalign 0.5
