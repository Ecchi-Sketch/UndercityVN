#// ------------------------------------------------------------------------------------------------
#// Crafting System - Clean Version
#// ------------------------------------------------------------------------------------------------
#// This file contains a clean crafting system implementation for Undercity.
#// Designed to prevent game advancement issues.
#// ------------------------------------------------------------------------------------------------

init python:
    # Recipe class definition
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
    
    # Recipe database
    recipe_database = {}

# Initialize recipes
label initialize_recipes:
    python:
        recipe_database["reinforced_vest"] = Recipe(
            id="reinforced_vest",
            name="Reinforced Vest",
            description="Craft a vest from leather and scrap metal.",
            ingredients={"scrap_metal": 3, "leather": 2},
            result_item_id="reinforced_vest",
            category="equippable"
        )
        
        recipe_database["healing_salve"] = Recipe(
            id="healing_salve",
            name="Healing Salve",
            description="A basic healing item that can restore a small amount of HP.",
            ingredients={"herb": 2, "cloth": 1},
            result_item_id="healing_salve",
            category="consumable"
        )
        
        recipe_database["advanced_shiv"] = Recipe(
            id="advanced_shiv",
            name="Advanced Shiv",
            description="A better version of the basic shiv.",
            ingredients={"makeshift_shiv": 1, "scrap_metal": 2},
            result_item_id="advanced_shiv",
            required_skill="new_kid_in_town",
            skill_level=2,
            category="equippable"
        )
    return

# NOTE: crafting_screen has been moved to character_sheet.rpy for proper modal behavior
