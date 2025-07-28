#// ------------------------------------------------------------------------------------------------
#// Character Sheet and HUD
#// ------------------------------------------------------------------------------------------------
#// The 'Learned Skills' screen now shows current/next level effects and has a button for a full upgrade tree.
#// ------------------------------------------------------------------------------------------------

# This python block defines a helper function that can be used by multiple screens in this file.
init python:
    # --- Function to format skill effects for display ---
    def get_effects_string(skill_obj, skill_level):
        if skill_level > skill_obj.max_level:
            return "N/A"
        effects = []
        for effect, base_value in skill_obj.base_effects.items():
            per_level_value = skill_obj.per_level_effects.get(effect, 0)
            total_bonus = base_value + (per_level_value * (skill_level - 1))
            
            formatted = ""
            if effect == "ac_bonus": formatted = "+{} AC".format(total_bonus)
            elif effect == "atk_bonus": formatted = "+{} ATK".format(total_bonus)
            elif effect == "dmg_bonus": formatted = "+{} DMG".format(total_bonus)
            effects.append(formatted)
        return ", ".join(effects)

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
        ymaximum 1500
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
                        text "Attributes" style "subheader_text"
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
                            text "ATK Bonus:" xsize 550 style "item_text"
                            text "+[player_stats.atk_bonus]" style "item_text"
                        hbox:
                            text "DMG Bonus:" xsize 550 style "item_text"
                            text "+[player_stats.dmg_bonus]" style "item_text"
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
                            text "Equipped Items" style "subheader_text"
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
                            text "Inventory" style "subheader_text"
                            
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
                        text "Active Effects"  style "subheader_text"
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
                        else:
                            text "Active - None"  style "inactive_text"
                            null

                        # --- Passive Skill Effects ---
                        text "Passive Effects" style "subheader_text"
                        null height 5
                        if player_stats.active_skills:
                            for skill_id in player_stats.active_skills:
                                python:
                                    skill = skill_database[skill_id]
                                    level = player_stats.learned_skills[skill_id]
                                    display_effects = get_effects_string(skill, level)
                                text "Passive Benefit - [skill.name]: [display_effects]" style "description_text"
                        else:
                            text "Passive - None"  style "inactive_text"
                        
                        null height 10
                        # Button to open the new skills management screen
                        textbutton "Manage Skills" action Show("learned_skills_screen") xalign 0.5


            else:
                text "Character data not yet available. Please complete character creation." xalign 0.5

# SCREEN for managing learned skills.
screen learned_skills_screen():
    modal True
    
    frame:
        xalign 0.5
        yalign 0.5
        xsize 1800
        padding (25, 25)

        vbox:
            spacing 15
            
            # --- Header ---
            hbox:
                textbutton "X" text_style "red_white_highlight_text" action Hide("learned_skills_screen") 
                text "Learned Skills"  style "subheader_text"
                

            add Solid("#404040", xfill=True, ysize=1)

            # --- Skills Viewport ---
            viewport:
                xsize 1750
                ysize 800
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
                                
                                upgrade_cost = player_stats.get_skill_upgrade_cost(skill_id)
                                can_afford = upgrade_cost is not None and player_stats.skill_xp >= upgrade_cost

                                current_effects = get_effects_string(skill, level)
                                next_level_effects = get_effects_string(skill, level + 1)

                            vbox:
                                spacing 5
                                hbox:                                 
                                    
                                    text "[skill.name] (Level [level]/[skill.max_level])" style "subheader_text"
                                    
                                    null
                                    #activate-deactivate
                                    textbutton toggle_button_text text_style "red_white_highlight_text" action Function(player_stats.toggle_skill, skill_id=skill.id)
                                
                                text "[skill.description]" style "description_text"

                                # --- Current and Next Level Effects Display ---
                                text "Current Effects: [current_effects]" style "item_text"
                                if level < skill.max_level:
                                    text "Next Level Effects: [next_level_effects]" style "item_text"

                                # --- Upgrade Button and Cost Display ---
                                if upgrade_cost is not None:
                                    hbox:
                                        text "Next Level Cost: [upgrade_cost] Skill XP" style "item_text"
                                        null
                                        #upgrade
                                        textbutton "Upgrade" text_style "green_to_blue" action Function(player_stats.level_up_skill, skill_id=skill.id) sensitive can_afford
                                else:
                                    text "Max Level Reached" style "item_text"

                                if level >= skill.max_level:
                                    text "Manifestation: [skill.manifestation_name]" bold True style "item_text"
                                    text "[skill.manifestation_desc]" style "description_text"
                                
                                # --- View Upgrade Tree Button ---
                                textbutton "View Upgrade Tree" text_style "inventory_button_text" action Show("skill_tree_screen", skill_id=skill.id)
                            
                            add Solid("#404040", xfill=True, ysize=1)
                    else:
                        text "You have not learned any skills yet." style "item_text"
                



# NEW SCREEN for viewing a skill's full upgrade tree.
screen skill_tree_screen(skill_id):
    modal True

    frame:
        xalign 0.5
        yalign 0.5
        xsize 1800
        padding (25, 25)

        vbox:
            spacing 15
            python:
                skill = skill_database[skill_id]

            # --- Header ---
            hbox:
                textbutton "X" text_style "red_white_highlight_text" action Hide("skill_tree_screen") xalign 1.0
                text "[skill.name] - Upgrade Tree"  style "subheader_text"
                
            
            add Solid("#404040", xfill=True, ysize=1)

            # --- Tree Viewport ---
            viewport:
                xsize 1750
                ysize 1000
                scrollbars "vertical"

                vbox:
                    spacing 8
                    # Loop from level 1 to the max level to show progression
                    for i in range(1, skill.max_level + 1):
                        python:
                            # Re-using the globally defined effect formatting function
                            display_effects = get_effects_string(skill, i)
                        
                        text "Level [i]: [display_effects]" style "item_text"
                    
                    # --- Manifestation Display ---
                    add Solid("#404040", xfill=True, ysize=1)
                    null height 5
                    text "Manifestation: [skill.manifestation_name]" bold True style "item_text"
                    text "[skill.manifestation_desc]" style "description_text"
