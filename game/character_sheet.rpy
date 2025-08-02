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
    
    # --- Function to get and format current node ID ---
    def get_current_node_display():
        """
        Gets current location display using centralized locations.rpy system.
        Returns formatted location string for character sheet display.
        """
        try:
            # Get current location node from centralized system
            location_node = get_current_location_node()
            
            # Return formatted display from the location node
            return location_node.get_formatted_display()
            
        except (AttributeError, NameError):
            return "Unknown Location"
    
    # --- Function to get player gender and pronouns ---
    def get_player_gender_display():
        """
        Gets player gender and pronoun information for character sheet display.
        Returns formatted string with gender and pronouns.
        """
        try:
            gender = getattr(player_stats, 'gender', 'Unspecified')
            pronouns = getattr(player_stats, 'pronouns', {'subject': 'they', 'object': 'them', 'possessive': 'their'})
            
            # Capitalize gender for display
            gender_display = gender.capitalize() if gender != 'unspecified' else 'Unspecified'
            pronoun_display = f"{pronouns['subject']}/{pronouns['object']}/{pronouns['possessive']}"
            
            return f"{gender_display} ({pronoun_display})"
            
        except (AttributeError, NameError):
            return "Unspecified (they/them/their)"

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
                        
                        # --- Current Location ---
                        null height 5
                        text "Current Location" style "subheader_text" size 24
                        vbox:
                            spacing 2
                            text "[get_current_node_display()]":
                                style "item_text"
                                size 20
                                color "#00CCFF"
                            text "(Node-based mapping system)":
                                style "description_text"
                                size 16
                                color "#888888"
                        
                        # --- Gender ---
                        null height 5
                        text "Gender" style "subheader_text" size 24
                        text "[get_player_gender_display()]":
                            style "item_text"
                            size 20
                            color "#FFB366"  # Orange color for gender display
                        
                        null height 10
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
                                            frame:
                                                background None
                                                padding (5, 5)
                                                vbox:
                                                    spacing 2
                                                    hbox:
                                                        text "{} (x{})".format(item.name, count) style "item_text"
                                                        null
                                                        if item.category == "equippable":
                                                            textbutton "Equip" text_style "inventory_button_text" action Function(player_stats.equip, item_id=item_id)
                                                        elif item.category == "consumable":
                                                            textbutton "Use" text_style "inventory_button_text" action Function(player_stats.use_consumable, item_id=item_id)
                                                    
                                                    # Create a concise mechanics description
                                                    $ mechanics_text = ""
                                                    
                                                    # Add cost info
                                                    if hasattr(item, "cost") and item.cost > 0:
                                                        $ mechanics_text += "Value: {} cogs. ".format(item.cost)
                                                    
                                                    # Add slot info for equippables
                                                    if item.category == "equippable" and hasattr(item, "slot"):
                                                        $ mechanics_text += "Slot: {}. ".format(item.slot.capitalize())
                                                    
                                                    # Add effects info
                                                    if hasattr(item, "effects") and item.effects:
                                                        $ mechanics_text += "Effects: "
                                                        $ effect_count = 0
                                                        for effect, value in item.effects.items():
                                                            $ effect_count += 1
                                                            if effect_count > 1:
                                                                $ mechanics_text += ", "
                                                            $ mechanics_text += "{}: {}".format(effect.replace("_", " ").capitalize(), value)
                                                    
                                                    # Add tags
                                                    if hasattr(item, "tags") and item.tags:
                                                        $ mechanics_text += " (" + ", ".join(item.tags) + ")"
                                                    
                                                    # Display mechanics text with a smaller font and different style
                                                    text "[mechanics_text]" style "description_text" size 18
                                    
                                    if not category_has_items:
                                        text "No items of this type." style "item_text"
                    add Solid("#404040", yfill=True, xsize=1)        


                    # --- RIGHT COLUMN (ACTIVE EFFECTS + BUTTONS SECTION) ---
                    vbox:
                        xsize 750
                        spacing 10
                        
                        # --- SECTION 1: ACTIVE EFFECTS ---
                        vbox:
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

                        # --- SECTION 2: PASSIVE EFFECTS ---
                        vbox:
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
                        
                        # Horizontal divider
                        add Solid("#404040", xfill=True, ysize=1)
                        
                        # --- SECTION 3: SKILLS & CRAFTING BUTTONS ---
                        vbox:
                            spacing 10
                            # Skills button
                            hbox:
                                xfill True
                                textbutton "Manage Skills" action ToggleScreen("learned_skills_screen") xalign 0.5
                            
                            # Horizontal divider
                            add Solid("#404040", xfill=True, ysize=1)
                            
                            # Crafting button - NEW TEMPLATE-BASED VERSION
                            hbox:
                                xfill True
                                textbutton "Crafting" action ToggleScreen("crafting_screen") xalign 0.5


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






# Feature-rich crafting screen - FIXED: craft_item no longer returns values
screen crafting_screen():
    modal True
    default recipe_category = "equippable"
    default have_ingredients_filter = False
    default have_skills_filter = False
    default inventory_tab = "equippable"
    
    frame:
        xalign 0.5
        yalign 0.5
        xsize 2560
        ysize 1500
        padding (20, 20)

        vbox:
            spacing 10
            
            # Header
            hbox:
                textbutton "X" text_style "red_white_highlight_text" action Hide("crafting_screen")
                text "Crafting" style "subheader_text"

            add Solid("#404040", xfill=True, ysize=1)

            # Main content area
            hbox:
                spacing 15
                
                # Left: Recipe list
                vbox:
                    xsize 1300
                    
                    # Recipe category tabs
                    hbox:
                    
                        spacing 0
                        text "Recipes:" style "subheader_text"
                    
                    hbox:
                    
                        spacing 0
                        #text "Recipes:" style "subheader_text"
                        textbutton "Equippable" action SetScreenVariable("recipe_category", "equippable") text_style "subheader_hover_text"
                        textbutton "Consumables" action SetScreenVariable("recipe_category", "consumable") text_style "subheader_hover_text"
                        textbutton "Plot" action SetScreenVariable("recipe_category", "plot") text_style "subheader_hover_text"
                        textbutton "Misc" action SetScreenVariable("recipe_category", "misc") text_style "subheader_hover_text"
                    
                    # Filters
                    hbox:
                        spacing 0
                        text "Filters:" style "subheader_text"
                                     
                    hbox:
                        spacing 0
                        #text "Filters:" style "subheader_text"
                        
                        textbutton "Have required ingredients" text_style "red_white_highlight_text" action ToggleScreenVariable("have_ingredients_filter")
                        text ("ON" if have_ingredients_filter else "OFF") style "green_to_blue"
                        
                            
                        textbutton "Have required skills/level" text_style "red_white_highlight_text" action ToggleScreenVariable("have_skills_filter")
                        text ("ON" if have_skills_filter else "OFF") style "green_to_blue"
                    
                    add Solid("#404040", xfill=True, ysize=1)
                    
                    # Recipes list
                    viewport:
                        xsize 1500
                        ysize 1350
                        scrollbars "vertical"
                        mousewheel True
                        
                        vbox:
                            spacing 8
                            
                            # Filter recipes by category and requirements
                            python:
                                filtered_recipes = []
                                category_has_recipes = False
                                
                                for recipe_id in recipe_database:
                                    recipe = recipe_database[recipe_id]
                                    
                                    # Filter by category
                                    if recipe.category != recipe_category:
                                        continue
                                        
                                    can_craft, reason = player_stats.can_craft(recipe_id)
                                    
                                    # Apply ingredient filter
                                    if have_ingredients_filter:
                                        have_all_ingredients = True
                                        for item_id, amount in recipe.ingredients.items():
                                            if player_stats.inventory.get(item_id, 0) < amount:
                                                have_all_ingredients = False
                                                break
                                                
                                        if not have_all_ingredients:
                                            continue
                                    
                                    # Apply skill filter
                                    if have_skills_filter and recipe.required_skill:
                                        if recipe.required_skill not in player_stats.learned_skills or player_stats.learned_skills[recipe.required_skill] < recipe.skill_level:
                                            continue
                                    
                                    # Add recipe to filtered list
                                    filtered_recipes.append(recipe_id)
                                    category_has_recipes = True
                            
                            # Display no recipes message if needed
                            if not category_has_recipes:
                                text "No recipes of this type available." style "inactive_text"
                            
                            # Display filtered recipes
                            for recipe_id in filtered_recipes:
                                python:
                                    recipe = recipe_database[recipe_id]
                                    can_craft, reason = player_stats.can_craft(recipe_id)
                                
                                frame:
                                    padding (10, 10)
                                    vbox:
                                        spacing 5
                                        text "[recipe.name]" style "subheader_text"
                                        text "[recipe.description]" style "description_text"
                                        
                                        if recipe.result_item_id in item_database:
                                            text "Creates: [item_database[recipe.result_item_id].name]" style "inactive_text"
                                        
                                        text "Ingredients:" style "subheader_text"
                                        for item_id, amount in recipe.ingredients.items():
                                            python:
                                                if item_id in item_database:
                                                    item_name = item_database[item_id].name
                                                    has_amount = player_stats.inventory.get(item_id, 0)
                                                    color = "inactive_text" if has_amount >= amount else "inactive_text"
                                                else:
                                                    item_name = "Unknown Item"
                                                    has_amount = 0
                                                    color = "inactive_text"
                                            text "- [item_name]: [has_amount]/[amount]" style color
                                        
                                        # FIXED Craft button - no return value, no advancement!
                                        if can_craft:
                                            textbutton "Craft"  action Function(player_stats.craft_item, recipe_id) xalign 0 text_style "craft_text"
                                        else:
                                            text "Cannot craft: [reason]" style "inactive_text" xalign 0.5
                
                add Solid("#404040", yfill=True, xsize=1)
                
                # Right: Inventory
                vbox:
                    xsize 1280
                    text "Your Inventory" style "subheader_text"
                    
                    # Inventory Category Tabs (matching the main inventory tabs)
                    hbox:
                        spacing 10
                        textbutton "Equippable" action SetScreenVariable("inventory_tab", "equippable") text_style "item_tab_text"
                        textbutton "Consumables" action SetScreenVariable("inventory_tab", "consumable") text_style "item_tab_text"
                        textbutton "Plot" action SetScreenVariable("inventory_tab", "plot") text_style "item_tab_text"
                        textbutton "Misc" action SetScreenVariable("inventory_tab", "misc") text_style "item_tab_text"
                    
                    viewport:
                        xsize 1200
                        ysize 1400
                        scrollbars "vertical"
                        mousewheel True
                        
                        vbox:
                            spacing 5
                            if player_stats.inventory:
                                python:
                                    # Filter inventory by category
                                    category_has_items = False
                                    for item_id in player_stats.inventory:
                                        if item_id in item_database and item_database[item_id].category == inventory_tab:
                                            category_has_items = True
                                            break
                                
                                python:
                                    # Filter and prepare inventory items in Python block
                                    filtered_inventory = []
                                    for item_id, count in player_stats.inventory.items():
                                        if item_id in item_database:
                                            item = item_database[item_id]
                                            # Only include items that match the selected category
                                            if item.category == inventory_tab:
                                                filtered_inventory.append((item_id, item, count))
                                        else:
                                            # Unknown items go into misc category
                                            if inventory_tab == "misc":
                                                filtered_inventory.append(("unknown", None, count))
                                
                                # Display the filtered items
                                for item_id, item, count in filtered_inventory:
                                    frame:
                                        background None
                                        padding (5, 5)
                                        vbox:
                                            spacing 2
                                            if item:
                                                text "[item.name] (x[count])" style "item_text"
                                                
                                                # Create a concise mechanics description
                                                $ mechanics_text = ""
                                                
                                                # Add cost info
                                                if item.cost > 0:
                                                    $ mechanics_text += "Value: {} cogs. ".format(item.cost)
                                                
                                                # Add slot info for equippables
                                                if item.category == "equippable" and hasattr(item, "slot"):
                                                    $ mechanics_text += "Slot: {}. ".format(item.slot.capitalize())
                                                
                                                # Add effects info
                                                if hasattr(item, "effects") and item.effects:
                                                    $ mechanics_text += "Effects: "
                                                    $ effect_count = 0
                                                    for effect, value in item.effects.items():
                                                        $ effect_count += 1
                                                        if effect_count > 1:
                                                            $ mechanics_text += ", "
                                                        $ mechanics_text += "{}: {}".format(effect.replace("_", " ").capitalize(), value)
                                                
                                                # Add tags
                                                if hasattr(item, "tags") and item.tags:
                                                    $ mechanics_text += " (" + ", ".join(item.tags) + ")"
                                                
                                                # Display mechanics text with a smaller font and different style
                                                text "[mechanics_text]" style "description_text" size 18
                                            else:
                                                text "Unknown Item (x[count])" style "item_text"
                                
                                if not category_has_items:
                                    text "No items of this type in inventory." style "inactive_text"
                            else:
                                text "Inventory is empty" style "inactive_text"
