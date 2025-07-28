#// ------------------------------------------------------------------------------------------------
#// Character Sheet and HUD
#// ------------------------------------------------------------------------------------------------
#// The new 'Learned Skills' screen now includes an 'Upgrade' button with cost display.
#// ------------------------------------------------------------------------------------------------
#// to add xp and skill xp
#// $ player_stats.gain_xp(base_amount=50, skill_amount=10)
#//

# Screen for the button that toggles the character sheet.
screen player_hud():
    zorder 100
    textbutton "Character" action ToggleScreen("player_stats_screen"):
        xalign 0.01
        yalign 0.01

# Screen for displaying player stats, inventory, and equipment.
screen player_stats_screen():
    default inventory_tab = "equippable"
    modal True

    frame:
        xalign 0.5
        yalign 0.5
        xsize 2560
        yminimum 600
        ymaximum 1580
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
                        xsize 550
                        spacing 10
                        text "Attributes" size 30
                        null height 5
                        # --- Core Stats ---
                        hbox:
                            text "Level:" xsize 150
                            text "[player_stats.level]"
                        hbox:
                            text "HP:" xsize 150
                            text "[player_stats.hp] / [player_stats.max_hp]"
                        hbox:
                            text "AC:" xsize 150
                            text "[player_stats.ac]"
                        hbox:
                            text "ATK Bonus:" xsize 150
                            text "+[player_stats.atk_bonus]"
                        hbox:
                            text "DMG Bonus:" xsize 150
                            text "+[player_stats.dmg_bonus]"
                        hbox:
                            text "Proficiency Bonus:" xsize 550 style "item_text"
                            text "+[player_stats.proficiency_bonus]" style "item_text"

                        null height 10

                        # --- XP Trackers ---
                        hbox:
                            text "Base XP: " xsize 250 style "item_text"
                            text "[player_stats.base_xp] / [player_stats.get_xp_for_next_level()]" style "item_text"
                        hbox:
                            text "Skill XP: " xsize 250 style "item_text"
                            text "[player_stats.skill_xp]" style "item_text"

                        null height 15

                        # --- Primary Attributes ---
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
                                    python:
                                        category_has_items = False
                                        for item_id in player_stats.inventory:
                                            if item_database[item_id].category == inventory_tab:
                                                category_has_items = True
                                                break
                                    
                                    for item_id, count in player_stats.inventory.items():
                                        python:
                                            item = item_database[item_id]

                                        if item.category == inventory_tab:
                                            hbox:
                                                text "{} (x{})".format(item.name, count) style "item_text"
                                                null
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
                                        if key == "ac_bonus": formatted_effect = "+{} AC".format(value)
                                        elif key == "max_hp_percent_bonus": formatted_effect = "+{}% Max HP".format(int(value * 100))
                                        elif key == "damage": formatted_effect = "Damage: {}".format(value)
                                        elif "_bonus" in key:
                                            stat_name = key.replace('_bonus', '').upper()
                                            formatted_effect = "+{} {}".format(value, stat_name)
                                        effects_str.append(formatted_effect)
                                    display_effects = ", ".join(effects_str)

                                text "Equipped - [item.name]: [display_effects]"  style "description_text"

                        # --- Passive Skill Effects ---
                        text "Passive Benefits" style "item_text"
                        null height 5
                        
                        if player_stats.active_skills:
                            for skill_id in player_stats.active_skills:
                                python:
                                    skill = skill_database[skill_id]
                                    level = player_stats.learned_skills[skill_id]
                                    effects_str = []
                                    for effect, base_value in skill.base_effects.items():
                                        per_level_value = skill.per_level_effects.get(effect, 0)
                                        total_bonus = base_value + (per_level_value * (level - 1))
                                        
                                        formatted_effect = ""
                                        if effect == "ac_bonus": formatted_effect = "+{} AC".format(total_bonus)
                                        elif effect == "atk_bonus": formatted_effect = "+{} ATK".format(total_bonus)
                                        elif effect == "dmg_bonus": formatted_effect = "+{} DMG".format(total_bonus)
                                        effects_str.append(formatted_effect)
                                    display_effects = ", ".join(effects_str)
                                text "Passive Benefit - [skill.name]: [display_effects]"   style "description_text"
                        else:
                            text "Passive Benefits"   style "description_text"
                        
                        null height 10
                        # Button to open the new skills management screen
                        textbutton "Manage Skills" action Show("learned_skills_screen") xalign 0.5


            else:
                text "Character data not yet available. Please complete character creation." xalign 0.5

# NEW SCREEN for managing learned skills.
screen learned_skills_screen():
    modal True
    
    frame:
        xalign 0.5
        yalign 0.5
        xsize 800
        padding (25, 25)

        vbox:
            spacing 15
            
            # --- Header ---
            hbox:
                text "Learned Skills" size 24 xalign 0.5
                textbutton "Close" action Hide("learned_skills_screen") xalign 1.0

            add Solid("#404040", xfill=True, ysize=1)

            # --- Skills Viewport ---
            viewport:
                xsize 750
                ysize 400
                scrollbars "vertical"
                mousewheel True

                vbox:
                    spacing 20
                    if player_stats.learned_skills:
                        for skill_id, level in player_stats.learned_skills.items():
                            python:
                                skill = skill_database[skill_id]
                                is_active = skill_id in player_stats.active_skills
                                toggle_button_text = "Deactivate" if is_active else "Activate"
                                
                                # Get the cost for the next level
                                upgrade_cost = player_stats.get_skill_upgrade_cost(skill_id)
                                can_afford = upgrade_cost is not None and player_stats.skill_xp >= upgrade_cost
                            
                            vbox:
                                spacing 5
                                hbox:
                                    text "[skill.name] (Level [level]/[skill.max_level])" size 20
                                    null
                                    textbutton toggle_button_text action Function(player_stats.toggle_skill, skill_id=skill.id)
                                
                                text "[skill.description]"

                                # --- Upgrade Button and Cost Display ---
                                if upgrade_cost is not None:
                                    hbox:
                                        text "Next Level Cost: [upgrade_cost] Skill XP"
                                        null
                                        # The button is only clickable if the player can afford the upgrade.
                                        textbutton "Upgrade" action Function(player_stats.level_up_skill, skill_id=skill.id) sensitive can_afford
                                else:
                                    text "Max Level Reached"

                                if level >= skill.max_level:
                                    text "Manifestation: [skill.manifestation_name]" bold True
                                    text "[skill.manifestation_desc]"
                    else:
                        text "You have not learned any skills yet."
