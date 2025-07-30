# This dictionary will hold all NPC stat blocks.
default npc_roster = {}

# Default base stats for NPCs - these are the baseline stats without equipment or skills
default default_npc_stats = {
    "zev": {
        "name": "Zev", 
        "hp": 12, 
        "ac": 12, 
        "str": 8, 
        "dex": 14, 
        "con": 10, 
        "intl": 12, 
        "wis": 14, 
        "cha": 10
    },
    "sevika": {
        "name": "Sevika", 
        "hp": 45, 
        "ac": 16, 
        "str": 18, 
        "dex": 14, 
        "con": 16, 
        "intl": 12, 
        "wis": 12, 
        "cha": 14
    },
    "zaunite_thug_template": {
        "name": "Zaunite Thug", 
        "hp": 15, 
        "ac": 13, 
        "str": 14, 
        "dex": 12, 
        "con": 12, 
        "intl": 8, 
        "wis": 8, 
        "cha": 8
    }
}

# NPC loadouts - equipment, skills, and abilities for each NPC
default npc_loadouts = {
    "zev": {
        # Equipment
        "equipment": {
            "weapon": "makeshift_shiv",
            "armor": None,
            "accessory": None,
            "inventory": ["scrap_metal", "cloth"]  # Additional items in inventory
        },
        # Skills (skill_id and level)
        "skills": {
            "scavenger": 1
        },
        # Which skills are active by default
        "active_skills": ["scavenger"]
    },
    
    "sevika": {
        "equipment": {
            "weapon": "iron_knuckles",
            "armor": "reinforced_vest",
            "accessory": "chem_stimulator",
            "inventory": ["healing_draught", "old_sewer_key"]
        },
        "skills": {
            "tough_as_nails": 3,
            "street_fighter": 2,
            "intimidation": 2
        },
        "active_skills": ["tough_as_nails", "street_fighter"]
    },
    
    "zaunite_thug_template": {
        "equipment": {
            "weapon": "makeshift_shiv",
            "armor": None,
            "accessory": None,
            "inventory": []
        },
        "skills": {
            "intimidation": 1
        },
        "active_skills": ["intimidation"]
    }
}

python early:
    def create_npc_with_loadout(npc_id, stats_dict=None):
        """
        Create a complete NPC with stats and loadout
        
        Parameters:
        - npc_id: The unique identifier for the NPC in the loadout dictionary
        - stats_dict: Optional dictionary of base stats; if not provided, loads from default_npc_stats
        
        Returns:
        - A fully configured CharacterStats object with equipment, skills and abilities
        """
        # If stats aren't provided, check if we have defaults for this NPC
        if stats_dict is None:
            if npc_id in default_npc_stats:
                stats_dict = default_npc_stats[npc_id]
            else:
                raise ValueError(f"No default stats found for NPC: {npc_id}")
        
        # Create the NPC with base stats
        npc = CharacterStats(**stats_dict)
        
        # Apply the loadout (equipment, skills, abilities)
        npc.apply_loadout(npc_id)
        
        return npc

# This label should be called once at the beginning of the game to populate the roster.
label initialize_npcs:
    # --- NPC ROSTER INITIALIZATION ---
    
    # ----- EXAMPLE 1: Simple usage with default stats -----
    # Create NPCs using their default stats and loadouts
    $ npc_roster["zev"] = create_npc_with_loadout("zev")
    
    # ----- EXAMPLE 2: Overriding default stats -----
    # Create an NPC with custom stats but standard loadout
    $ npc_roster["sevika"] = create_npc_with_loadout("sevika", {
        "name": "Sevika (Elite)", 
        "hp": 55,  # Higher HP than default
        "ac": 18,  # Higher AC than default
        "str": 20, # Higher strength than default
        "dex": 14, 
        "con": 16, 
        "intl": 12, 
        "wis": 12, 
        "cha": 16  # Higher charisma than default
    })
    
    # ----- EXAMPLE 3: Creating variants from templates -----
    # Create a custom NPC based on the thug template
    $ npc_roster["zaunite_enforcer"] = create_npc_with_loadout("zaunite_thug_template", {
        "name": "Zaunite Enforcer",  # New name
        "hp": 25,                     # Higher HP than template
        "str": 16                     # Higher strength than template
    })
    
    # ----- EXAMPLE 4: Mass creation of NPCs from a template -----
    # This shows how to create multiple variants at once
    python:
        for i, name in enumerate(["Thug A", "Thug B", "Thug C"]):
            npc_id = f"zaunite_thug_{i}"
            stats = default_npc_stats["zaunite_thug_template"].copy()
            stats["name"] = name
            # You could customize each one here if needed
            npc_roster[npc_id] = create_npc_with_loadout("zaunite_thug_template", stats)
    
    return

# ----- HOW TO USE THE NPC LOADOUT SYSTEM -----
# 
# 1. Define NPC base stats in default_npc_stats dictionary
# 2. Define equipment and skills in npc_loadouts dictionary
# 3. Use create_npc_with_loadout() to create NPCs with their loadouts
#
# ----- ADDING A NEW NPC -----
# 
# # Step 1: Add default stats
# default default_npc_stats["new_npc_id"] = {
#     "name": "NPC Name", 
#     "hp": 20, 
#     "ac": 14, 
#     "str": 12, 
#     "dex": 12, 
#     "con": 12, 
#     "intl": 12, 
#     "wis": 12, 
#     "cha": 12
# }
#
# # Step 2: Define loadout (equipment, skills, etc)
# default npc_loadouts["new_npc_id"] = {
#     "equipment": {
#         "weapon": "item_id_here",
#         "armor": "item_id_here",
#         "accessory": None,  # None for empty slots
#         "inventory": ["item_1", "item_2"]
#     },
#     "skills": {
#         "skill_id_1": 2,  # Level 2 in this skill
#         "skill_id_2": 1   # Level 1 in this skill
#     },
#     "active_skills": ["skill_id_1"]  # Only this skill is active by default
# }
#
# # Step 3: Create the NPC in initialize_npcs label
# $ npc_roster["new_npc_id"] = create_npc_with_loadout("new_npc_id")
#
# # Or create a variant with custom stats
# $ npc_roster["npc_variant"] = create_npc_with_loadout("new_npc_id", {
#     "name": "Custom Name",
#     "hp": 30  # Override just the HP
# })
#
