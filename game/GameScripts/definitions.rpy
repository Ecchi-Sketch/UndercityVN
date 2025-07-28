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

            # Inventory and Equipment attributes
            self.inventory = []
            self.equipped_items = [] # A simple list for all equipped items

        def equip(self, item_to_equip):
            # Move the item from inventory to equipped list
            if item_to_equip in self.inventory:
                self.inventory.remove(item_to_equip)
                self.equipped_items.append(item_to_equip)
                self.recalculate_stats()

        def unequip(self, item_to_unequip):
            # Move the item from equipped list back to inventory
            if item_to_unequip in self.equipped_items:
                self.equipped_items.remove(item_to_unequip)
                self.inventory.append(item_to_unequip)
                self.recalculate_stats()

        def recalculate_stats(self):
            # Reset stats to their base values before applying item effects
            self.max_hp = self.base_max_hp
            self.ac = self.base_ac

            # Apply effects from all equipped items
            for item in self.equipped_items:
                if "ac_bonus" in item.effects:
                    self.ac += item.effects["ac_bonus"]
                if "max_hp_percent_bonus" in item.effects:
                    # Calculate bonus based on base HP to prevent runaway stacking
                    hp_bonus = int(self.base_max_hp * item.effects["max_hp_percent_bonus"])
                    self.max_hp += hp_bonus

            # Ensure current HP doesn't exceed the new max HP
            if self.hp > self.max_hp:
                self.hp = self.max_hp

        # A helper function to calculate the d20 modifier for an attribute.
        def get_modifier(self, attribute):
            attr_value = getattr(self, attribute.lower())
            return (attr_value - 10) // 2

        # A helper function to create a unique copy of this character.
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

style description_text is default:
    size 30
    color "#aaddff" # A light blue color for stats
    bold True
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
