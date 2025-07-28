# This python early block defines the core data structure for all characters.
# Placing it here ensures it's loaded before other scripts that use it.
python early:
    # We define a Python class to hold all the character's TTRPG stats.
    # This can be used for the Player and for all NPCs.
    class CharacterStats:
        def __init__(self, name, hp, ac, str, dex, con, intl, wis, cha):
            self.name = name

            self.max_hp = hp
            self.hp = hp
            self.ac = ac

            # d20 Core Attributes
            self.strength = str
            self.dexterity = dex
            self.constitution = con
            self.intelligence = intl
            self.wisdom = wis
            self.charisma = cha

        # A helper function to calculate the d20 modifier for an attribute.
        # The formula is (Attribute - 10) / 2, rounded down.
        def get_modifier(self, attribute):
            attr_value = getattr(self, attribute.lower())
            return (attr_value - 10) // 2

        # A helper function to create a unique copy of this character.
        # This is essential for creating multiple enemies from a single template.
        def copy(self):
            return CharacterStats(self.name, self.max_hp, self.ac, self.strength, self.dexterity, self.constitution, self.intelligence, self.wisdom, self.charisma)


# == 0. Style Definitions =====================================================
# This section defines the visual styles for text elements on the screens.
# You can adjust properties like size, color, and boldness here.

# -- Adjust the 'size' property below to change the font size for large headers.
style header is default:
    size 36
    bold True
    color "#FFFFFF"
    outlines [ (1, "#000000", 0, 0) ]

# -- Adjust the 'size' property below to change the font size for body text (summaries, stats, etc.).
style body_text is default:
    size 22

# == 1. Character Definitions =================================================
# The 'Character' object takes the name to be displayed and can have other properties
# like 'color' to change the name's text color in the dialogue box.

define player = Character("[player_name]")
define enforcer = Character("Stern Enforcer", color="#aaddff")
define crew_boss = Character("Crew Boss", color="#c8a8a8")
define auth_voice = Character("Authoritative Voice", color="#e0a0a0")
define crewman = Character("Young Crewman", color="#c8c8a8")
define scrim = Character("Scrim", color="#ff6666") # Using thug color
define zev = Character("Zev", color="#cc9900")
define gage = Character("Gage", color="#ff7777")
define rella = Character("Rella", color="#ff8888")
define alchemist = Character("Alley Alchemist", color="#aaffaa")
define vex = Character("Vex", color="#a832a8")
define jaxom = Character("'Augment-Arm' Jaxom", color="#ffaa88")
define bouncer = Character("Bouncer", color="#c0c0c0")


# == 2. Image and Asset Placeholders ==========================================
# It's good practice to define your images at the top.
# Replace these with your actual file names (e.g., "images/backgrounds/cargo_hold.jpg")
image bg_cargo_hold = "placeholder_bg.png"
image bg_docks = "placeholder_bg.png"
image bg_north_bridge = "placeholder_bg.png"
image bg_alcove_district = "placeholder_bg.png"
image bg_last_drop_interior = "placeholder_bg.png"
image bg_last_drop_balcony = "placeholder_bg.png"
image bg_alchemist_lab = "placeholder_bg.png"
image bg_wreckage_site = "placeholder_bg.png"
image bg_zevs_hovel = "placeholder_bg.png"
image bg_char_creation = "placeholder_bg.png" # Background for creation screen

image enforcer_silhouette = "placeholder_character.png"
image enforcer_guard = "placeholder_character.png"
image enforcer_stern = "placeholder_character.png"
image vex_smirking = "placeholder_character.png"
image jaxom_angry = "placeholder_character.png"
image bouncer_stoic = "placeholder_character.png"
