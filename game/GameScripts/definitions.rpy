# This python early block defines the core data structure for all characters.
# Placing it here ensures it's loaded before other scripts that use it.
python early:
    # We define a Python class to hold all the character's TTRPG stats.
    # This can be used for the Player and for all NPCs.
    class CharacterStats:
        def __init__(self, name, hp, ac, str, dex, con, intl, wis, cha):
            self.name = name

            # Base stats that should not change after character creation.
            self.base_max_hp = hp
            self.base_ac = ac

            # d20 Core Attributes
            self.strength = str
            self.dexterity = dex
            self.constitution = con
            self.intelligence = intl
            self.wisdom = wis
            self.charisma = cha

            # Current, calculated stats that will be modified by effects.
            self.max_hp = self.base_max_hp
            self.hp = self.base_max_hp # Start with full health
            self.ac = self.base_ac

            # --- INVENTORY OVERHAUL ---
            # The inventory is now a dictionary to handle item stacks.
            # The key is the item's unique ID (from item_database), and the value is the quantity.
            self.inventory = {}
            # Equipped items remains a list of the actual Item objects.
            self.equipped_items = []

        # NEW: The primary function for adding items to the inventory.
        def add_item(self, item_id, amount=1):
            # If the item is already in the inventory, just increase the count.
            if item_id in self.inventory:
                self.inventory[item_id] += amount
            # Otherwise, add it to the inventory with the specified amount.
            else:
                self.inventory[item_id] = amount

        def equip(self, item_id):
            # Check if the item exists in inventory and is equippable.
            if item_id in self.inventory and item_database[item_id].category == "equippable":
                # Decrease the item count in inventory.
                self.inventory[item_id] -= 1
                # If the count drops to 0, remove it from the inventory entirely.
                if self.inventory[item_id] == 0:
                    del self.inventory[item_id]
                
                # Add the actual Item object to the equipped list.
                self.equipped_items.append(item_database[item_id])
                self.recalculate_stats()

        def unequip(self, item_to_unequip):
            # Find the item's unique ID.
            item_id = next((key for key, value in item_database.items() if value == item_to_unequip), None)
            if item_id and item_to_unequip in self.equipped_items:
                # Remove the item from the equipped list.
                self.equipped_items.remove(item_to_unequip)
                # Add it back to the inventory, stacking if it already exists.
                self.add_item(item_id, 1)
                self.recalculate_stats()

        def use_consumable(self, item_id):
            # Check if the item exists in inventory and is a consumable.
            if item_id in self.inventory and item_database[item_id].category == "consumable":
                item_to_use = item_database[item_id]
                # Apply effects.
                if "heal_amount" in item_to_use.effects:
                    self.hp += item_to_use.effects["heal_amount"]
                    if self.hp > self.max_hp:
                        self.hp = self.max_hp
                
                # Decrease the item count and remove if it reaches 0.
                self.inventory[item_id] -= 1
                if self.inventory[item_id] == 0:
                    del self.inventory[item_id]

        def recalculate_stats(self):
            # Reset stats to their base values before applying item effects.
            self.max_hp = self.base_max_hp
            self.ac = self.base_ac

            # Apply effects from all equipped items.
            for item in self.equipped_items:
                if "ac_bonus" in item.effects:
                    self.ac += item.effects["ac_bonus"]
                if "max_hp_percent_bonus" in item.effects:
                    hp_bonus = int(self.base_max_hp * item.effects["max_hp_percent_bonus"])
                    self.max_hp += hp_bonus

            if self.hp > self.max_hp:
                self.hp = self.max_hp

        def get_modifier(self, attribute):
            attr_value = getattr(self, attribute.lower())
            return (attr_value - 10) // 2

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

style item_tab_text is default:
    size 50
    color "#FFFFFF" # A light blue color for stats
    bold True
    hover_color "#aaddff"
    # You can add other properties like fonts, outlines, etc.

style description_text is default:
    size 30
    color "#aaddff" # A light blue color for stats
    bold True
    # You can add other properties like fonts, outlines, etc.

style red_white_highlight_text is default:
    size 30
    color "#ff2a00" # A light blue color for stats
    bold True
    hover_color "#ffffff"
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
