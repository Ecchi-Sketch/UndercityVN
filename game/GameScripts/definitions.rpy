# This python early block defines the core data structures for all characters, items, and skills.
# Placing all class definitions here ensures they are loaded before any other scripts that use them.
python early:
    #==========================================================================
    # CLASS DEFINITIONS
    #==========================================================================

    # Defines a game item, including its properties and effects.
    class Item:
        def __init__(self, name, description, category="misc", slot=None, effects=None, cost=0, tags=None):
            self.name = name
            self.description = description
            self.category = category
            self.slot = slot
            self.effects = effects if effects is not None else {}
            self.cost = cost
            self.tags = tags if tags is not None else []

    # Defines a skill, its effects, and how it scales with levels.
    class LearnedSkill:
        def __init__(self, id, name, description, max_level, base_effects, per_level_effects, manifestation_name, manifestation_desc):
            self.id = id
            self.name = name
            self.description = description
            self.max_level = max_level
            self.base_effects = base_effects
            self.per_level_effects = per_level_effects
            self.manifestation_name = manifestation_name
            self.manifestation_desc = manifestation_desc

    # Defines a crafting recipe.
    class Recipe:
        def __init__(self, id, name, description, ingredients, result_item_id, result_amount=1, required_skill=None, skill_level=None, category=None):
            self.id = id
            self.name = name
            self.description = description
            self.ingredients = ingredients
            self.result_item_id = result_item_id
            self.result_amount = result_amount
            self.required_skill = required_skill
            self.skill_level = skill_level
            self.category = category or "misc"

    # This dictionary stores the total XP needed to reach the start of each level.
    xp_thresholds = {
        1: 0, 2: 300, 3: 900, 4: 2700, 5: 6500, 6: 14000, 7: 23000,
        8: 34000, 9: 48000, 10: 64000, 11: 85000, 12: 100000, 13: 120000,
        14: 140000, 15: 165000, 16: 195000, 17: 225000, 18: 265000,
        19: 305000, 20: 355000
    }

    # This dictionary stores the total Skill XP required to reach a given skill level.
    skill_level_costs = {
        1: 0, 2: 100, 3: 300, 4: 600, 5: 1000, 6: 1500, 7: 2100, 8: 2800, 9: 3600, 10: 4500
    }

    # The primary class for holding all character TTRPG stats.
    class CharacterStats:
        def __init__(self, name, hp, ac, str, dex, con, intl, wis, cha, description="", backstory="", fighting_style=""):
            self.name = name
            self.is_player = False

            self.base_max_hp = hp
            self.base_ac = ac
            self.base_atk_bonus = 0
            self.base_dmg_bonus = 0

            self.strength = str
            self.dexterity = dex
            self.constitution = con
            self.intelligence = intl
            self.wisdom = wis
            self.charisma = cha

            self.max_hp = self.base_max_hp
            self.hp = self.base_max_hp
            self.ac = self.base_ac
            self.atk_bonus = self.base_atk_bonus
            self.dmg_bonus = self.base_dmg_bonus

            self.inventory = {}
            self.equipped_items = []

            self.level = 1
            self.base_xp = 0
            self.skill_xp = 0
            self.proficiency_bonus = 2
            
            # Grit system - player-only resource for additional actions
            self.max_grit_points = 1 + ((self.level - 1) // 4)  # +1 every 4 levels
            self.grit_points = self.max_grit_points
            
            self.learned_skills = {}
            self.active_skills = []
            
            self.description = description
            self.backstory = backstory
            self.fighting_style = fighting_style
            self.is_dynamic = False
            self.creation_timestamp = None
            
        def apply_loadout(self, npc_id):
            if npc_id in npc_loadouts:
                loadout = npc_loadouts[npc_id]
                if "equipment" in loadout:
                    equipment = loadout["equipment"]
                    for slot, item_id in equipment.items():
                        if slot != "inventory" and item_id is not None:
                            self.add_item(item_id)
                            self.equip(item_id)
                    for item_id in equipment.get("inventory", []):
                        self.add_item(item_id)
                if "skills" in loadout:
                    for skill_id, level in loadout["skills"].items():
                        if skill_id not in self.learned_skills:
                            self.learned_skills[skill_id] = 0
                        while self.learned_skills[skill_id] < level:
                            self.learned_skills[skill_id] += 1
                if "active_skills" in loadout:
                    self.active_skills = []
                    for skill_id in loadout["active_skills"]:
                        if skill_id in self.learned_skills:
                            self.active_skills.append(skill_id)
                self.recalculate_stats()

        def recalculate_stats(self):
            self.max_hp = self.base_max_hp
            self.ac = self.base_ac
            self.atk_bonus = self.base_atk_bonus
            self.dmg_bonus = self.base_dmg_bonus
            for item in self.equipped_items:
                if "ac_bonus" in item.effects: self.ac += item.effects["ac_bonus"]
                if "atk_bonus" in item.effects: self.atk_bonus += item.effects["atk_bonus"]
                if "dmg_bonus" in item.effects: self.dmg_bonus += item.effects["dmg_bonus"]
                if "max_hp_percent_bonus" in item.effects:
                    self.max_hp += int(self.base_max_hp * item.effects["max_hp_percent_bonus"])
            for skill_id in self.active_skills:
                if skill_id in self.learned_skills and skill_id in skill_database:
                    skill = skill_database[skill_id]
                    level = self.learned_skills[skill_id]
                    for effect, base_value in skill.base_effects.items():
                        per_level_value = skill.per_level_effects.get(effect, 0)
                        total_bonus = base_value + (per_level_value * (level - 1))
                        if effect == "ac_bonus": self.ac += total_bonus
                        if effect == "atk_bonus": self.atk_bonus += total_bonus
                        if effect == "dmg_bonus": self.dmg_bonus += total_bonus
            if self.hp > self.max_hp:
                self.hp = self.max_hp

        def learn_skill(self, skill_id):
            if skill_id not in self.learned_skills:
                self.learned_skills[skill_id] = 1
                if skill_id not in self.active_skills:
                    self.active_skills.append(skill_id)
                self.recalculate_stats()

        def get_skill_upgrade_cost(self, skill_id):
            if skill_id in self.learned_skills and skill_id in skill_database:
                current_level = self.learned_skills[skill_id]
                skill = skill_database[skill_id]
                if current_level < skill.max_level:
                    return skill_level_costs.get(current_level + 1)
            return None

        def level_up_skill(self, skill_id):
            cost = self.get_skill_upgrade_cost(skill_id)
            if cost is not None and self.skill_xp >= cost:
                self.learned_skills[skill_id] += 1
                self.skill_xp -= cost
                self.recalculate_stats()

        def toggle_skill(self, skill_id):
            """Toggle a learned skill between active and inactive states"""
            if skill_id in self.learned_skills:
                if skill_id in self.active_skills:
                    # Deactivate the skill
                    self.active_skills.remove(skill_id)
                else:
                    # Activate the skill
                    self.active_skills.append(skill_id)
                # Recalculate stats since active skills affect character stats
                self.recalculate_stats()

        def can_craft(self, recipe_id):
            """Check if a recipe can be crafted and return reason if not"""
            if recipe_id not in recipe_database:
                return False, "Recipe not found"
            
            recipe = recipe_database[recipe_id]
            
            # Check if required skill is met
            if recipe.required_skill:
                if recipe.required_skill not in self.learned_skills:
                    return False, f"Requires {skill_database[recipe.required_skill].name if recipe.required_skill in skill_database else recipe.required_skill} skill"
                if self.learned_skills[recipe.required_skill] < recipe.skill_level:
                    return False, f"Requires {skill_database[recipe.required_skill].name if recipe.required_skill in skill_database else recipe.required_skill} level {recipe.skill_level}"
            
            # Check if all ingredients are available
            for item_id, required_amount in recipe.ingredients.items():
                available_amount = self.inventory.get(item_id, 0)
                if available_amount < required_amount:
                    item_name = item_database[item_id].name if item_id in item_database else item_id
                    return False, f"Need {required_amount - available_amount} more {item_name}"
            
            return True, ""

        def craft_item(self, recipe_id):
            """Craft an item if possible - does not return value to prevent game advancement"""
            can_craft, reason = self.can_craft(recipe_id)
            if not can_craft:
                renpy.notify(f"Cannot craft: {reason}")
                return  # No return value to prevent dialogue advancement
            
            recipe = recipe_database[recipe_id]
            
            # Remove ingredients from inventory
            for item_id, required_amount in recipe.ingredients.items():
                self.inventory[item_id] -= required_amount
                if self.inventory[item_id] == 0:
                    del self.inventory[item_id]
            
            # Add crafted item to inventory
            self.add_item(recipe.result_item_id, recipe.result_amount)
            
            # Notify player of successful crafting
            item_name = item_database[recipe.result_item_id].name if recipe.result_item_id in item_database else recipe.result_item_id
            renpy.notify(f"Crafted {recipe.result_amount}x {item_name}!")
            # No return value to prevent dialogue advancement

        def add_item(self, item_id, amount=1):
            if item_id in self.inventory: self.inventory[item_id] += amount
            else: self.inventory[item_id] = amount

        def equip(self, item_id):
            if item_id in self.inventory and item_id in item_database and item_database[item_id].category == "equippable":
                self.inventory[item_id] -= 1
                if self.inventory[item_id] == 0: del self.inventory[item_id]
                self.equipped_items.append(item_database[item_id])
                self.recalculate_stats()

        def unequip(self, item_to_unequip):
            item_id = next((key for key, value in item_database.items() if value == item_to_unequip), None)
            if item_id and item_to_unequip in self.equipped_items:
                self.equipped_items.remove(item_to_unequip)
                self.add_item(item_id, 1)
                self.recalculate_stats()
        
        def use_consumable(self, item_id):
            """Use a consumable item and apply its effects"""
            if item_id in self.inventory and item_id in item_database:
                item = item_database[item_id]
                if item.category == "consumable":
                    # Remove one from inventory
                    self.inventory[item_id] -= 1
                    if self.inventory[item_id] == 0:
                        del self.inventory[item_id]
                    
                    # Apply item effects
                    if item.effects:
                        for effect, value in item.effects.items():
                            if effect == "heal" or effect == "heal_amount":
                                # Heal the character
                                combat_manager = get_combat_manager()
                                
                                # CRITICAL FIX: Use combat HP if in combat, otherwise use character HP
                                if combat_manager:
                                    # Find the player's combatant to get the correct current HP
                                    player_combatant = None
                                    for combatant in combat_manager.turn_order:
                                        if getattr(combatant.character_data, 'is_player', False):
                                            player_combatant = combatant
                                            break
                                    
                                    if player_combatant:
                                        old_hp = player_combatant.current_hp
                                        combat_manager._log_event({
                                            "event_type": "consumable_debug",
                                            "message": "DEBUG: Combat HP: {}/{}, Healing Value: {}".format(old_hp, self.max_hp, value)
                                        })
                                        
                                        # Apply healing to combat HP
                                        new_hp = min(self.max_hp, old_hp + value)
                                        healed = new_hp - old_hp
                                        
                                        # Update both combat and character HP
                                        player_combatant.current_hp = new_hp
                                        self.hp = new_hp
                                        
                                        combat_manager._log_event({
                                            "event_type": "consumable_debug",
                                            "message": "DEBUG: Healed {} HP. New HP: {}/{}".format(healed, new_hp, self.max_hp)
                                        })
                                    else:
                                        # Fallback to character HP if combatant not found
                                        old_hp = self.hp
                                        self.hp = min(self.max_hp, self.hp + value)
                                        healed = self.hp - old_hp
                                else:
                                    # Not in combat, use character HP normally
                                    old_hp = self.hp
                                    self.hp = min(self.max_hp, self.hp + value)
                                    healed = self.hp - old_hp
                                
                                # Log healing calculation debug to combat log
                                if combat_manager:
                                    combat_manager._log_event({
                                        "event_type": "consumable_debug",
                                        "message": "DEBUG: Old HP: {}, New HP: {}, Healed: {}".format(old_hp, self.hp, healed)
                                    })
                                
                                # Log healing result to combat log
                                if combat_manager:
                                    if healed > 0:
                                        combat_manager._log_event({
                                            "event_type": "healing",
                                            "message": "Healed {} HP! ({}/{} HP)".format(healed, self.hp, self.max_hp),
                                            "healed_amount": healed,
                                            "current_hp": self.hp,
                                            "max_hp": self.max_hp
                                        })
                                    else:
                                        combat_manager._log_event({
                                            "event_type": "healing",
                                            "message": "Already at full health!"
                                        })
                                else:
                                    # Fallback to renpy.notify if not in combat
                                    if healed > 0:
                                        renpy.notify("Healed {} HP! ({}/{} HP)".format(healed, self.hp, self.max_hp))
                                    else:
                                        renpy.notify("Already at full health!")
                            # Add other consumable effects here as needed
                    
                    # Return nothing to prevent game advancement
                    return
            # Return nothing to prevent game advancement
        
        def spend_grit_point(self):
            """Spend a grit point if available. Returns True if successful, False if no grit available."""
            if self.grit_points > 0:
                self.grit_points -= 1
                return True
            return False
        
        def restore_grit_points(self):
            """Restore grit points to maximum (for rest/recovery)"""
            self.grit_points = self.max_grit_points
        
        def get_xp_for_next_level(self):
            return xp_thresholds.get(self.level + 1, 999999)

        def gain_xp(self, base_amount=0, skill_amount=0):
            self.base_xp += base_amount
            self.skill_xp += skill_amount
            self.check_for_level_up()

        def check_for_level_up(self):
            while self.base_xp >= self.get_xp_for_next_level():
                self.level += 1
                self.proficiency_bonus = 2 + ((self.level - 1) // 4)
                # Update grit points when leveling up (same timing as proficiency bonus)
                new_max_grit = 1 + ((self.level - 1) // 4)
                if new_max_grit > self.max_grit_points:
                    self.max_grit_points = new_max_grit
                    self.grit_points = self.max_grit_points  # Restore to full on level up

#==============================================================================
# STYLES & DIALOGUE CHARACTER DEFINITIONS
#==============================================================================
style header is default:
    size 36
    bold True
    color "#FFFFFF"
    outlines [ (1, "#000000", 0, 0) ]

style body_text is default:
    size 22

style equipped_item_text is default:
    size 50
    color "#aaddff"
    bold True

style item_text is default:
    size 50
    color "#FFFFFF"
    bold False

style subheader_text is default:
    size 40
    color "#898989"
    bold True

style combat_mechanical_text is default:
    size 30
    color "#FFFFFF"
    bold True

style log_body_text is default:
    size 32
    color "#FFFFFF"
    bold False

style combat_bonus_text is default:
    size 28
    color "#FFFFFF"
    bold True

style combat_mechanical_text_sub1 is default:
    size 25
    color "#FFFFFF"
    bold False

style combat_stats_text is default:
    size 25
    color "#FFFFFF"
    bold True

style subheader_hover_text is default:
    size 40
    color "#898989"
    bold True
    hover_color "#ffffff"

style item_tab_text is default:
    size 40
    color "#aaddff"
    bold True
    hover_color "#ffffff"

style description_text is default:
    size 30
    color "#aaddff"
    bold True

style inactive_text is default:
    size 30
    color "#dfdfdf"
    bold False

style skill_upgrade_text is default:
    size 40
    color "#72aacf"
    bold True

style craft_text is default:
    size 40
    color "#79aa88"
    bold True
    hover_color "#aaddff"

style red_white_highlight_text is default:
    size 30
    color "#ff2a00"
    bold True
    hover_color "#ffffff"

style green_to_blue is default:
    size 30
    color "#79aa88"
    bold True
    hover_color "#aaddff"

style white_to_blue is default:
    size 30
    color "#ffffff"
    bold True
    hover_color "#aaddff"    

style inventory_button_text is default:
    size 30
    color "#aaddff"
    xalign 1.0 
    hover_color "#ffffff"


# == 1. Character Definitions =================================================
define player = Character("[player_name]")
define enforcer = Character("Stern Enforcer", color="#aaddff")
define crew_boss = Character("Crew Boss", color="#c8a8a8")
define auth_voice = Character("Authoritative Voice", color="#e0a0a0")
define crewman = Character("Young Crewman", color="#c8c8a8")
define scrim = Character("Scrim", color="#ff6666")
define zev = Character("Zev", color="#cc9900")
define gage = Character("Gage", color="#ff7777")
define rella = Character("Rella", color="#ff8888")
define alchemist = Character("Alley Alchemist", color="#aaffaa")
define vex = Character("Vex", color="#a832a8")
define jaxom = Character("'Augment-Arm' Jaxom", color="#ffaa88")
define bouncer = Character("Bouncer", color="#c0c0c0")


# == 2. Image and Asset Placeholders ==========================================
image bg_cargo_hold = "placeholder_bg.png"
image bg_docks = "placeholder_bg.png"
image bg_north_bridge = "placeholder_bg.png"
image bg_alcove_district = "placeholder_bg.png"
image bg_last_drop_interior = "placeholder_bg.png"
image bg_last_drop_balcony = "placeholder_bg.png"
image bg_alchemist_lab = "placeholder_bg.png"
image bg_wreckage_site = "placeholder_bg.png"
image bg_zevs_hovel = "placeholder_bg.png"
image bg_char_creation = "placeholder_bg.png"

image enforcer_silhouette = "placeholder_character.png"
image enforcer_guard = "placeholder_character.png"
image enforcer_stern = "placeholder_character.png"
image vex_smirking = "placeholder_character.png"
image jaxom_angry = "placeholder_character.png"
image bouncer_stoic = "placeholder_character.png"
