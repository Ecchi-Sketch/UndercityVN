#// ------------------------------------------------------------------------------------------------
#// Item Definitions
#// ------------------------------------------------------------------------------------------------
#// This file defines the base class for all items and creates a database of
#// all available items in the game.
#// ------------------------------------------------------------------------------------------------

init python:
    # The base class for all items in the game.
    class Item:
        def __init__(self, name, description, slot, effects=None):
            self.name = name
            self.description = description
            # The slot determines where the item can be equipped (e.g., "weapon", "armor").
            self.slot = slot
            # The effects dictionary stores the mechanical benefits of the item.
            self.effects = effects if effects is not None else {}

    # This dictionary will hold all defined items for easy access.
    # We can fetch an item by its key, e.g., item_database["shiv"]
    item_database = {}

# This label should be called once at the start of the game to populate the database.
label initialize_items:
    python:
        # --- WEAPONS ---
        item_database["makeshift_shiv"] = Item(
            name="Makeshift Shiv",
            description="A sharpened piece of scrap metal. It's not much, but it's pointy.",
            slot="weapon",
            effects={"damage": "1d4"} # A small, concealable weapon
        )

        item_database["iron_knuckles"] = Item(
            name="Iron Knuckles",
            description="Heavy iron knuckles that add significant weight to a punch.",
            slot="weapon",
            effects={"damage": "1d6"}
        )

        # --- ARMOR ---
        item_database["reinforced_vest"] = Item(
            name="Reinforced Vest",
            description="A heavy leather vest reinforced with scavenged metal plates.",
            slot="armor",
            effects={"ac_bonus": 2}
        )

        # --- ACCESSORIES ---
        item_database["chem_stimulator"] = Item(
            name="Volatile Chem-Stimulator",
            description="A crude device that injects a cocktail of stimulants, temporarily boosting vitality.",
            slot="accessory",
            effects={"max_hp_percent_bonus": 0.5} # 50% increase to max HP
        )
    return
