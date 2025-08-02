#// ------------------------------------------------------------------------------------------------
#// Item Definitions
#// ------------------------------------------------------------------------------------------------
#// The Item class has been updated to include a 'category' attribute.
#// Categories are: 'equippable', 'consumable', 'plot', and 'misc'.
#// ------------------------------------------------------------------------------------------------

#// ------------------------------------------------------------------------------------------------
#// ITEM TEMPLATE - Copy and paste this block to create a new item.
#// ------------------------------------------------------------------------------------------------
#   # --- [CATEGORY NAME] ---
#   item_database["[item_id]"] = Item(
#       name="[Item Name]",
#       description="[A brief description of the item.]",
#       category="[equippable/consumable/plot/misc]",
#       # The 'slot' is only needed for 'equippable' items.
#       slot="[weapon/armor/accessory]",
#       # The 'effects' dictionary holds all mechanical bonuses.
#       effects={"[effect_name]": [value], "[another_effect]": "[value]"}
#   )
#// ------------------------------------------------------------------------------------------------


init python:
    # The base class for all items in the game.
    class Item:
        """Class representing an item in the game."""
        # The 'slot' is now optional, as other categories don't need one.
        def __init__(self, name, description, category="misc", slot=None, effects=None, cost=0, tags=None):
            self.name = name
            self.description = description
            self.category = category # "equippable", "consumable", "plot", "misc"
            self.slot = slot
            self.effects = effects if effects is not None else {}
            self.cost = cost
            
            # Default tags to match the category if not provided
            if tags is None:
                if category == "equippable":
                    self.tags = ["Equippable"]
                elif category == "consumable":
                    self.tags = ["Consumable"]
                elif category == "plot":
                    self.tags = ["Plot"]
                else:
                    self.tags = ["Misc"]
            else:
                self.tags = tags

    # This dictionary will hold all defined items for easy access.
    item_database = {}

# This label should be called once at the start of the game to populate the database.
label initialize_items:
    python:
        # --- EQUIPPABLE: WEAPONS ---
        item_database["makeshift_shiv"] = Item(
            name="Makeshift Shiv",
            description="A sharpened piece of scrap metal. It's not much, but it's pointy.",
            category="equippable",
            slot="weapon",
            effects={"damage": "1d4"},
            cost=5,
            tags=["Equippable", "Weapon", "Melee"]
        )
        

    #============================================================================
    # Character Specific Items
    #============================================================================
    
        item_database["sevikas_puncher"] = Item(
            name="Sevika's Puncher",
            description="A shimmer-infused prosthetic arm, befitting for Silco's top enforcer.",
            category="equippable",
            slot="weapon",
            effects={"damage": "1d10"},
            cost=0,
            tags=["Sevika", "Weapon", "Melee", "Plot"]
        )


    #============================================================================
    # Common Items
    #============================================================================


        # --- EQUIPPABLE: ARMOR ---
        item_database["reinforced_vest"] = Item(
            name="Reinforced Vest",
            description="A leather vest reinforced with scrap metal. Provides basic protection.",
            category="equippable",
            slot="armor",
            effects={"ac_bonus": 2},
            cost=15,
            tags=["Equippable", "Armor", "Protection"]
        )
        
        # --- EQUIPPABLE: WEAPONS ---
        item_database["advanced_shiv"] = Item(
            name="Advanced Shiv",
            description="An improved version of the makeshift shiv with better grip and balance.",
            category="equippable",
            slot="weapon",
            effects={"damage": "1d6", "atk_bonus": 1},
            cost=10,
            tags=["Equippable", "Weapon", "Melee", "Advanced"]
        )
        
        # --- CONSUMABLE ---
        item_database["healing_salve"] = Item(
            name="Healing Salve",
            description="A basic healing item that can restore a small amount of HP.",
            category="consumable",
            effects={"heal": 10},
            cost=8,
            tags=["Consumable", "Healing", "Medical"]
        )
        
        # --- CRAFTING INGREDIENTS ---
        item_database["scrap_metal"] = Item(
            name="Scrap Metal",
            description="Small pieces of metal scavenged from around the undercity. Useful for crafting.",
            category="misc",
            cost=3,
            tags=["Misc", "Crafting", "Material"]
        )
        
        item_database["leather"] = Item(
            name="Leather",
            description="Scraps of leather that can be used for crafting various items.",
            category="misc",
            cost=5,
            tags=["Misc", "Crafting", "Material"]
        )
        
        item_database["herb"] = Item(
            name="Common Herb",
            description="A common plant with mild medicinal properties. Used in basic healing items.",
            category="misc",
            cost=2,
            tags=["Misc", "Crafting", "Herb", "Medical"]
        )
        
        item_database["cloth"] = Item(
            name="Cloth",
            description="Simple cloth scraps. Useful for crafting and bandaging wounds.",
            category="misc",
            cost=2,
            tags=["Misc", "Crafting", "Material"]
        )

        item_database["iron_knuckles"] = Item(
            name="Iron Knuckles",
            description="Heavy iron knuckles that add significant weight to a punch.",
            category="equippable",
            slot="weapon",
            effects={"damage": "1d6"},
            cost=12,
            tags=["Equippable", "Weapon", "Melee"]
        )

        # --- EQUIPPABLE: ARMOR ---
        item_database["reinforced_vest"] = Item(
            name="Reinforced Vest",
            description="A heavy leather vest reinforced with scavenged metal plates.",
            category="equippable",
            slot="armor",
            effects={"ac_bonus": 2},
            cost=15,
            tags=["Equippable", "Armor", "Protection"]
        )

        # --- EQUIPPABLE: ACCESSORIES ---
        item_database["chem_stimulator"] = Item(
            name="Volatile Chem-Stimulator",
            description="A crude device that injects a cocktail of stimulants, temporarily boosting vitality.",
            category="equippable",
            slot="accessory",
            effects={"max_hp_percent_bonus": 0.5},
            cost=20,
            tags=["Equippable", "Accessory", "Enhancement"]
        )
        
        # --- CONSUMABLES ---
        item_database["healing_draught"] = Item(
            name="Healing Draught",
            description="A vial of shimmering green liquid that restores a small amount of health.",
            category="consumable",
            effects={"heal_amount": 10},
            cost=15,
            tags=["Consumable", "Healing", "Medical", "Potion"]
        )

        # --- PLOT ITEMS ---
        item_database["old_sewer_key"] = Item(
            name="Old Sewer Key",
            description="A heavy, rust-covered iron key. Seems important.",
            category="plot",
            cost=0,
            tags=["Plot", "Key"]
        )

        # --- MISCELLANEOUS ITEMS ---
        
        # --- DISCOVERABLE ITEMS ---
        
        # Normal Discovery Items
        item_database["scrap_metal"] = Item(
            name="Scrap Metal",
            description="Twisted pieces of metal that could be useful for crafting.",
            category="misc",
            cost=3,
            tags=["Misc", "Crafting", "Material", "discover_normal"]
        )
        
        item_database["old_bolt"] = Item(
            name="Old Bolt",
            description="A rusty but still functional bolt. Common salvage in Zaun.",
            category="misc",
            cost=1,
            tags=["Misc", "Crafting", "Material", "discover_normal"]
        )
        
        item_database["worn_leather"] = Item(
            name="Worn Leather",
            description="Weathered leather scraps, still usable for repairs.",
            category="misc",
            cost=4,
            tags=["Misc", "Crafting", "Material", "discover_normal"]
        )
        
        # Rare Discovery Items
        item_database["shimmer_residue"] = Item(
            name="Shimmer Residue",
            description="Crystallized shimmer that enhances physical capabilities temporarily.",
            category="consumable",
            effects={"str_temp_bonus": 2, "duration": 3},
            cost=25,
            tags=["Consumable", "Enhancement", "Shimmer", "discover_rare"]
        )
        
        item_database["hextech_fragment"] = Item(
            name="Hextech Fragment",
            description="A small piece of hextech crystal that pulses with magical energy.",
            category="misc",
            cost=50,
            tags=["Misc", "Magical", "Hextech", "Valuable", "discover_rare"]
        )
        
        item_database["precision_tools"] = Item(
            name="Precision Tools",
            description="High-quality tools that aid in detailed work and investigation.",
            category="equippable",
            slot="accessory",
            effects={"discovery_bonus": 2},
            cost=35,
            tags=["Equippable", "Accessory", "Investigation", "discover_rare"]
        )
        
        # Epic Discovery Items
        item_database["zaun_relic"] = Item(
            name="Ancient Zaun Relic",
            description="A mysterious artifact from old Zaun, humming with unknown power.",
            category="equippable",
            slot="accessory",
            effects={"discovery_advantage": True, "max_hp_bonus": 5},
            cost=100,
            tags=["Equippable", "Accessory", "Relic", "Magical", "discover_epic"]
        )
        
        item_database["master_lockpick"] = Item(
            name="Master's Lockpick Set",
            description="Legendary lockpicks used by the greatest thieves of Zaun.",
            category="equippable",
            slot="accessory",
            effects={"discovery_bonus": 3, "stealth_bonus": 2},
            cost=75,
            tags=["Equippable", "Accessory", "Legendary", "Thievery", "discover_epic"]
        )
        
        item_database["pure_shimmer_vial"] = Item(
            name="Pure Shimmer Vial",
            description="An incredibly rare vial of pure, uncut shimmer.",
            category="consumable",
            effects={"heal_amount": 25, "str_temp_bonus": 3, "duration": 5},
            cost=150,
            tags=["Consumable", "Healing", "Enhancement", "Shimmer", "Legendary", "discover_epic"]
        )

    return
