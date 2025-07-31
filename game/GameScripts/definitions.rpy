# This python early block defines the core data structure for all characters.
# Placing it here ensures it's loaded before other scripts that use it.
python early:
    # This dictionary stores the total XP needed to reach the start of each level.
    xp_thresholds = {
        1: 0, 2: 300, 3: 900, 4: 2700, 5: 6500, 6: 14000, 7: 23000,
        8: 34000, 9: 48000, 10: 64000, 11: 85000, 12: 100000, 13: 120000,
        14: 140000, 15: 165000, 16: 195000, 17: 225000, 18: 265000,
        19: 305000, 20: 355000
    }

    # NEW: This dictionary stores the total Skill XP required to reach a given skill level.
    skill_level_costs = {
        1: 0, 2: 100, 3: 300, 4: 600, 5: 1000, 6: 1500, 7: 2100, 8: 2800, 9: 3600, 10: 4500
    }

    # We define a Python class to hold all the character's TTRPG stats.
    class CharacterStats:
        def __init__(self, name, hp, ac, str, dex, con, intl, wis, cha, description="", backstory="", fighting_style=""):
            self.name = name

            # Base stats
            self.base_max_hp = hp
            self.base_ac = ac
            self.base_atk_bonus = 0
            self.base_dmg_bonus = 0

            # Core Attributes
            self.strength = str
            self.dexterity = dex
            self.constitution = con
            self.intelligence = intl
            self.wisdom = wis
            self.charisma = cha

            # Current, calculated stats
            self.max_hp = self.base_max_hp
            self.hp = self.base_max_hp
            self.ac = self.base_ac
            self.atk_bonus = self.base_atk_bonus
            self.dmg_bonus = self.base_dmg_bonus

            # Inventory and Equipment
            self.inventory = {}
            self.equipped_items = []

            # XP and Leveling
            self.level = 1
            self.base_xp = 0
            self.skill_xp = 10000
            self.proficiency_bonus = 2
            
            # Learned Skills
            self.learned_skills = {} # Stores skill IDs and their current level, e.g., {"new_kid_in_town": 1}
            self.active_skills = [] # A list of skill IDs that are currently toggled on.
            
            # Extended fields for dynamic NPCs
            self.description = description        # Physical description
            self.backstory = backstory           # Character background
            self.fighting_style = fighting_style # Combat style description
            self.is_dynamic = False             # Flag for dynamically created NPCs
            self.creation_timestamp = None      # When this NPC was created
            
        def apply_loadout(self, npc_id):
            """Apply equipment, skills, and abilities loadout for an NPC"""
            if npc_id in npc_loadouts:
                loadout = npc_loadouts[npc_id]
                
                # Apply equipment
                if "equipment" in loadout:
                    equipment = loadout["equipment"]
                    
                    # Equip gear
                    for slot, item_id in equipment.items():
                        if slot != "inventory" and item_id is not None:
                            # Add item to inventory first
                            self.add_item(item_id)
                            # Then equip it
                            self.equip(item_id)
                    
                    # Add inventory items
                    for item_id in equipment.get("inventory", []):
                        self.add_item(item_id)
                
                # Apply skills
                if "skills" in loadout:
                    for skill_id, level in loadout["skills"].items():
                        # First learn the skill at level 1
                        if skill_id not in self.learned_skills:
                            self.learned_skills[skill_id] = 1
                            
                        # Then level it up to desired level
                        while self.learned_skills[skill_id] < level:
                            self.learned_skills[skill_id] += 1
                
                # Set active skills
                if "active_skills" in loadout:
                    # Reset active skills to only those defined in loadout
                    self.active_skills = []
                    for skill_id in loadout["active_skills"]:
                        if skill_id in self.learned_skills:
                            self.active_skills.append(skill_id)
                
                # Finally recalculate stats to apply all bonuses
                self.recalculate_stats()

        # --- SKILL FUNCTIONS ---
        def learn_skill(self, skill_id):
            if skill_id not in self.learned_skills:
                self.learned_skills[skill_id] = 1
                self.active_skills.append(skill_id) # Activate skill by default when learned
                self.recalculate_stats()

        def toggle_skill(self, skill_id):
            if skill_id in self.active_skills:
                self.active_skills.remove(skill_id)
            elif skill_id in self.learned_skills:
                self.active_skills.append(skill_id)
            self.recalculate_stats()
        
        # NEW: Helper function to get the cost for the next level of a skill.
        def get_skill_upgrade_cost(self, skill_id):
            if skill_id in self.learned_skills:
                current_level = self.learned_skills[skill_id]
                skill = skill_database[skill_id]
                if current_level < skill.max_level:
                    return skill_level_costs.get(current_level + 1)
            return None # Return None if skill is max level or not learned

        def level_up_skill(self, skill_id):
            cost = self.get_skill_upgrade_cost(skill_id)
            # Check if the skill can be leveled up and if the player has enough total Skill XP.
            if cost is not None and self.skill_xp >= cost:
                self.learned_skills[skill_id] += 1
                self.skill_xp -= cost  # Deduct the cost from skill XP
                self.recalculate_stats()

        # --- STAT RECALCULATION ---
        def recalculate_stats(self):
            # 1. Reset stats to their base values
            self.max_hp = self.base_max_hp
            self.ac = self.base_ac
            self.atk_bonus = self.base_atk_bonus
            self.dmg_bonus = self.base_dmg_bonus

            # 2. Apply effects from equipped items
            for item in self.equipped_items:
                if "ac_bonus" in item.effects: self.ac += item.effects["ac_bonus"]
                if "atk_bonus" in item.effects: self.atk_bonus += item.effects["atk_bonus"]
                if "dmg_bonus" in item.effects: self.dmg_bonus += item.effects["dmg_bonus"]
                if "max_hp_percent_bonus" in item.effects:
                    self.max_hp += int(self.base_max_hp * item.effects["max_hp_percent_bonus"])

            # 3. Apply effects from active skills
            for skill_id in self.active_skills:
                if skill_id in self.learned_skills:
                    skill = skill_database[skill_id]
                    level = self.learned_skills[skill_id]
                    
        # --- CRAFTING METHODS ---
        def can_craft(self, recipe_id):
            if recipe_id not in recipe_database:
                return False, "Recipe not found"
                
            recipe = recipe_database[recipe_id]
            
            # Check if player has required skill (if any)
            if recipe.required_skill and (
                recipe.required_skill not in self.learned_skills or 
                self.learned_skills[recipe.required_skill] < recipe.skill_level
            ):
                return False, "Required skill not learned or insufficient level"
            
            # Check if player has all ingredients
            for item_id, amount in recipe.ingredients.items():
                if item_id not in self.inventory or self.inventory[item_id] < amount:
                    return False, "Missing ingredients"
                    
            return True, "Can craft"

        def craft_item(self, recipe_id):
            can_craft, reason = self.can_craft(recipe_id)
            if not can_craft:
                return  # Exit early if can't craft, return None like toggle_skill
            
            recipe = recipe_database[recipe_id]
            
            # Remove ingredients
            for item_id, amount in recipe.ingredients.items():
                self.inventory[item_id] -= amount
                if self.inventory[item_id] <= 0:
                    del self.inventory[item_id]
            
            # Add crafted item
            self.add_item(recipe.result_item_id, recipe.result_amount)
            
            # Grant XP for crafting
            self.gain_xp(skill_amount=10)
            
            # TEST: No return value, just like working toggle_skill function
            
        # --- STAT CALCULATION CONTINUED ---
        def _apply_skill_effects(self):
            # 3. Apply effects from active skills
            for skill_id in self.active_skills:
                if skill_id in self.learned_skills:
                    skill = skill_database[skill_id]
                    level = self.learned_skills[skill_id]
                    # Calculate total bonus: base + (per_level * (level - 1))
                    for effect, base_value in skill.base_effects.items():
                        per_level_value = skill.per_level_effects.get(effect, 0)
                        total_bonus = base_value + (per_level_value * (level - 1))
                        
                        if effect == "ac_bonus": self.ac += total_bonus
                        if effect == "atk_bonus": self.atk_bonus += total_bonus
                        if effect == "dmg_bonus": self.dmg_bonus += total_bonus

            # Ensure current HP doesn't exceed the new max HP
            if self.hp > self.max_hp:
                self.hp = self.max_hp

        # Other functions...
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

        def add_item(self, item_id, amount=1):
            if item_id in self.inventory: self.inventory[item_id] += amount
            else: self.inventory[item_id] = amount

        def equip(self, item_id):
            if item_id in self.inventory and item_database[item_id].category == "equippable":
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
            if item_id in self.inventory and item_database[item_id].category == "consumable":
                item_to_use = item_database[item_id]
                if "heal_amount" in item_to_use.effects:
                    self.hp += item_to_use.effects["heal_amount"]
                    if self.hp > self.max_hp: self.hp = self.max_hp
                self.inventory[item_id] -= 1
                if self.inventory[item_id] == 0: del self.inventory[item_id]

        def get_modifier(self, attribute):
            return (getattr(self, attribute.lower()) - 10) // 2

        def copy(self):
            return CharacterStats(self.name, self.base_max_hp, self.base_ac, self.strength, self.dexterity, self.constitution, self.intelligence, self.wisdom, self.charisma)


# == 0. Style Definitions =====================================================
# This section defines the visual styles for text elements on the screens.
style header is default:
    size 36
    bold True
    color "#FFFFFF"
    outlines [ (1, "#000000", 0, 0) ]

style body_text is default:
    size 22

# Add this to definitions.rpy with your other styles

style equipped_item_text is default:
    size 50
    color "#aaddff" # A light blue color for stats
    bold True
    # You can add other properties like fonts, outlines, etc.

style item_text is default:
    size 50
    color "#FFFFFF" # white
    bold False
#    hover_color "#aaddff"
    # You can add other properties like fonts, outlines, etc.

style subheader_text is default:
    size 40
    color "#898989" # gray
    bold True
#    hover_color "#aaddff"
    # You can add other properties like fonts, outlines, etc.

style combat_mechanical_text is default:
    size 30
    color "#FFFFFF" # White
    bold True
#    hover_color "#aaddff"
    # You can add other properties like fonts, outlines, etc.

style combat_mechanical_text_sub1 is default:
    size 25
    color "#FFFFFF" # White
    bold False
#    hover_color "#aaddff"
    # You can add other properties like fonts, outlines, etc.

style combat_stats_text is default:
    size 25
    color "#FFFFFF" # White
    bold True
#    hover_color "#aaddff"
    # You can add other properties like fonts, outlines, etc.

style subheader_hover_text is default:
    size 40
    color "#898989" # gray
    bold True
    hover_color "#ffffff" # white
    # You can add other properties like fonts, outlines, etc.

style item_tab_text is default:
    size 40
    color "#aaddff" # A light blue color for stats
    bold True
    hover_color "#ffffff"
    # You can add other properties like fonts, outlines, etc.

style description_text is default:
    size 30
    color "#aaddff" # A light blue color for stats
    bold True
    # You can add other properties like fonts, outlines, etc.

style inactive_text is default:
    size 30
    color "#dfdfdf" # gray
    bold False
    # You can add other properties like fonts, outlines, etc.

style skill_upgrade_text is default:
    size 40
    color "#72aacf" # blue
    bold True
    # You can add other properties like fonts, outlines, etc.

style craft_text is default:
    size 40
    color "#79aa88" # green
    bold True
    hover_color "#aaddff"
    # You can add other properties like fonts, outlines, etc.

style red_white_highlight_text is default:
    size 30
    color "#ff2a00" # A light blue color for stats
    bold True
    hover_color "#ffffff"
    # You can add other properties like fonts, outlines, etc.

style green_to_blue is default:
    size 30
    color "#79aa88" # green
    bold True
    hover_color "#aaddff"
    # You can add other properties like fonts, outlines, etc.




style inventory_button_text is default:
    # This 'size' property will now correctly target the button's text
    size 30
    color "#aaddff"
    xalign 1.0 
    # This property changes the text color when the button is hovered
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
