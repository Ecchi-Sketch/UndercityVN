# This dictionary will hold all NPC stat blocks.
default npc_roster = {}

# Default base stats for NPCs - these are the baseline stats without equipment or skills
# Now includes description and backstory for LLM-enhanced combat narratives
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
        "cha": 10,
        "gender": "male",
        "pronouns": {"subject": "he", "object": "him", "possessive": "his"},
        "description": "A small, wiry scavenger with quick eyes and nimble fingers. Zev moves with the fluid grace of someone who's spent years dodging danger in Zaun's cramped alleys. His clothes are patched and practical, with hidden pockets for tools and found treasures.",
        "backstory": "Zev grew up in the Gray, learning to survive by salvaging useful materials from Zaun's industrial waste. He's developed an uncanny ability to spot valuable scrap and avoid the worst dangers of the undercity. Despite his rough upbringing, Zev maintains an optimistic outlook and genuine curiosity about the world.",
        "fighting_style": "Evasive Scavenger - relies on speed, dirty tricks, and improvised weapons"
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
        "cha": 14,
        "gender": "female",
        "pronouns": {"subject": "she", "object": "her", "possessive": "her"},
        "description": "A towering, intimidating figure with a cybernetic left arm that gleams with deadly purpose. Sevika's muscular frame is covered in scars from countless battles, and her cold eyes show no mercy. Her mechanical arm whirs softly with each movement, a constant reminder of her enhanced lethality.",
        "backstory": "Sevika lost her left arm defending Zaun from Piltovan enforcers, but gained something far more dangerous in return. Now serving as Silco's right hand, she enforces order in the undercity through brutal efficiency. Her loyalty to Zaun runs deeper than blood, and she'll crush anyone who threatens her home.",
        "fighting_style": "Cybernetic Brawler - overwhelming strength combined with mechanical precision"
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
        "cha": 8,
        "gender": "male",
        "pronouns": {"subject": "he", "object": "him", "possessive": "his"},
        "description": "A rough-looking street fighter with multiple scars and gang tattoos. His clothes are torn and stained with the grime of Zaun's streets. Cold, desperate eyes hint at a life of violence and survival at any cost.",
        "backstory": "Another casualty of Zaun's harsh reality, forced into violence by poverty and desperation. He's learned that in the undercity, you either fight or become prey. His loyalty can be bought, but his desperation makes him dangerous and unpredictable.",
        "fighting_style": "Street Brawler - dirty fighting with improvised weapons and no honor"
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
            "weapon": "sevikas_puncher",
            "armor": "reinforced_vest",
            "accessory": "chem_stimulator",
            "inventory": ["healing_draught", "old_sewer_key"]
        },
        "skills": {
            "tough_as_nails": 1,
            "street_fighter": 1,
            "intimidation": 1
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
    },
    # Player loadout is now defined here to ensure it exists before being used.
    "player_loadout": {
        "equipment": {
            "weapon": "makeshift_shiv",
            "armor": None,
            "accessory": None,
            "inventory": ["healing_draught", "scrap_metal"]
        },
        "skills": {
            "street_fighter": 1,
            "new_kid_in_town": 1
        },
        "active_skills": ["street_fighter", "new_kid_in_town"]
    }
}

#==============================================================================
# PLAYER CHARACTER DEFINITION
#==============================================================================
# The player object is now defined here as 'player_stats' to align with
# character_sheet.rpy and to resolve the load order error. This is the one
# and only 'default' definition for this variable.
default player_stats = CharacterStats(
    name="Player",
    hp=50,
    ac=14,
    str=14,
    dex=14,
    con=14,
    intl=10,
    wis=10,
    cha=10
)

label initialize_player_character:
    python:
        player_stats.is_player = True
        player_stats.apply_loadout("player_loadout")
    return

#==============================================================================
# NPC CREATION LOGIC
#==============================================================================

python early:
    def create_npc_with_loadout(npc_id, stats_dict=None):
        """
        Create a complete NPC with stats and loadout
        
        Parameters:
        - npc_id: The unique identifier for the NPC in the loadout dictionary
        - stats_dict: Optional dictionary of base stats; if not provided, loads from default_npc_stats
                     If provided, these will OVERRIDE the base template stats, not replace them entirely
        
        Returns:
        - A fully configured CharacterStats object with equipment, skills and abilities
        """
        # Start with base template stats
        if npc_id in default_npc_stats:
            base_stats = default_npc_stats[npc_id].copy()  # Copy to avoid modifying original
        else:
            raise ValueError(f"No default stats found for NPC template: {npc_id}")
        
        # If custom stats are provided, merge them with the base stats
        if stats_dict is not None:
            base_stats.update(stats_dict)  # Override base stats with custom ones
        
        # Create the NPC with merged stats
        npc = CharacterStats(
            name=base_stats.get("name"),
            hp=base_stats.get("hp"),
            ac=base_stats.get("ac"),
            str=base_stats.get("str"),
            dex=base_stats.get("dex"),
            con=base_stats.get("con"),
            intl=base_stats.get("intl"),
            wis=base_stats.get("wis"),
            cha=base_stats.get("cha")
        )
        
        # Apply the loadout (equipment, skills, abilities)
        npc.apply_loadout(npc_id)
        
        return npc

# This label should be called once at the beginning of the game to populate the roster.
label initialize_npcs:
    # --- NPC ROSTER INITIALIZATION ---
    
    # ----- EXAMPLE 1: Simple usage with default stats -----
    # Create NPCs using their default stats and loadouts
    $ npc_roster["zev"] = create_npc_with_loadout("zev")
    $ npc_roster["sevika"] = create_npc_with_loadout("sevika")

    # ----- EXAMPLE 2: Overriding default stats -----
    # Create an NPC with custom stats but standard loadout
    #$ npc_roster["sevika"] = create_npc_with_loadout("sevika", {
    #    "name": "Sevika (Elite)", 
    #    "hp": 55,  # Higher HP than default
    #    "ac": 18,  # Higher AC than default
    #    "str": 20, # Higher strength than default
    #    "dex": 14, 
    #    "con": 16, 
    #    "intl": 12, 
    #    "wis": 12, 
    #    "cha": 16  # Higher charisma than default
    #})
    
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

#============================================================================
# DYNAMIC NPC CREATION SYSTEM
#============================================================================
# This system allows creating NPCs dynamically during gameplay for battles,
# encounters, or story events. All dynamic NPCs are automatically saved
# and persist across game sessions.

# Storage for dynamically created NPCs (automatically saved/loaded by Ren'Py)
default dynamic_npcs = {}

# Templates for generating different types of NPCs quickly
default npc_generation_templates = {
    "street_tough": {
        "base_template": "zaunite_thug_template",
        "name_pool": ["Razor", "Scar", "Brick", "Venom", "Grit", "Slash", "Knuckles", "Steel"],
        "description_templates": [
            "A rough-looking street fighter with multiple scars across their face",
            "A lean and dangerous-looking thug with cold, calculating eyes",
            "A muscular enforcer with gang tattoos covering their arms",
            "A wiry fighter with quick movements and a predatory stance"
        ],
        "backstory_templates": [
            "Grew up fighting in the streets of Zaun for survival",
            "Former pit fighter turned street enforcer",
            "A desperate soul who turned to violence to feed their family",
            "Once worked the mines until an accident forced them into crime"
        ],
        "fighting_style_pool": ["Brawler", "Street Fighter", "Dirty Fighter", "Scrapper"],
        "equipment_variants": [
            {"weapon": "makeshift_shiv", "armor": None, "accessory": None},
            {"weapon": "iron_knuckles", "armor": None, "accessory": None},
            {"weapon": "makeshift_shiv", "armor": "reinforced_vest", "accessory": None}
        ]
    },
    "elite_enforcer": {
        "base_template": "sevika",
        "name_pool": ["Captain Kane", "Commander Steel", "Boss Iron", "Lieutenant Vex", "Sergeant Crusher"],
        "description_templates": [
            "An imposing figure in reinforced armor with cybernetic enhancements",
            "A battle-scarred veteran with augmented limbs and cold metal eyes",
            "A towering enforcer whose presence alone commands respect and fear"
        ],
        "backstory_templates": [
            "Rose through the ranks of Silco's organization through brutal efficiency",
            "A former Piltovan guard who fell from grace and embraced the undercity",
            "Survived the chemical wars and emerged stronger, deadlier"
        ],
        "fighting_style_pool": ["Heavy Brawler", "Tactical Fighter", "Cybernetic Combatant"],
        "stat_boosts": {"hp": 15, "str": 3, "ac": 2},
        "guaranteed_equipment": {"armor": "reinforced_vest", "accessory": "chem_stimulator"}
    },
    "nimble_scout": {
        "base_template": "zev",
        "name_pool": ["Shadow", "Whisper", "Dash", "Swift", "Ghost", "Flicker"],
        "description_templates": [
            "A small, quick figure who moves like smoke through the shadows",
            "An agile scout with keen eyes and silent footsteps",
            "A wiry individual dressed in dark, practical clothing"
        ],
        "backstory_templates": [
            "Learned to survive by staying unseen in Zaun's dangerous streets",
            "Former messenger who knows every secret passage in the undercity",
            "A refugee who developed incredible stealth skills to avoid gangs"
        ],
        "fighting_style_pool": ["Hit and Run", "Stealth Fighter", "Evasive Combatant"],
        "stat_boosts": {"dex": 4, "wis": 2},
        "equipment_variants": [
            {"weapon": "makeshift_shiv", "armor": None, "accessory": None}
        ]
    }
}

python early:
    import time
    import random

    def create_dynamic_npc(template_id=None, custom_data=None):
        """
        Create a dynamic NPC for battle situations or story encounters
        
        Parameters:
        - template_id: Base template to use (e.g., "zaunite_thug_template")
        - custom_data: Dictionary with custom overrides for stats, description, etc.
        
        Returns:
        - Tuple of (unique_id, npc_object) - The NPC is automatically stored in dynamic_npcs
        """
        timestamp = str(int(time.time() * 1000))
        unique_id = f"dynamic_npc_{timestamp}"
        
        if template_id and template_id in default_npc_stats:
            base_stats = default_npc_stats[template_id].copy()
            base_loadout = npc_loadouts.get(template_id, {}).copy() if template_id in npc_loadouts else {}
        else:
            base_stats = {
                "name": "Unknown Fighter", "hp": 15, "ac": 12, "str": 12, "dex": 12, "con": 12,
                "intl": 10, "wis": 10, "cha": 10
            }
            base_loadout = {
                "equipment": {"weapon": "makeshift_shiv", "armor": None, "accessory": None, "inventory": []},
                "skills": {}, "active_skills": []
            }
        
        if custom_data:
            if "stats" in custom_data:
                base_stats.update(custom_data["stats"])
            if "loadout" in custom_data:
                custom_loadout = custom_data["loadout"]
                if "equipment" in custom_loadout:
                    if "equipment" not in base_loadout: base_loadout["equipment"] = {}
                    base_loadout["equipment"].update(custom_loadout["equipment"])
                if "skills" in custom_loadout:
                    if "skills" not in base_loadout: base_loadout["skills"] = {}
                    base_loadout["skills"].update(custom_loadout["skills"])
                if "active_skills" in custom_loadout:
                    base_loadout["active_skills"] = custom_loadout["active_skills"]
        
        npc = CharacterStats(
            name=base_stats.get("name", "Unknown Fighter"), hp=base_stats.get("hp", 15),
            ac=base_stats.get("ac", 12), str=base_stats.get("str", 12), dex=base_stats.get("dex", 12),
            con=base_stats.get("con", 12), intl=base_stats.get("intl", 10), wis=base_stats.get("wis", 10),
            cha=base_stats.get("cha", 10), description=custom_data.get("description", "") if custom_data else "",
            backstory=custom_data.get("backstory", "") if custom_data else "",
            fighting_style=custom_data.get("fighting_style", "") if custom_data else ""
        )
        
        npc.is_dynamic = True
        npc.creation_timestamp = timestamp
        
        if base_loadout:
            temp_loadouts = npc_loadouts.copy()
            temp_loadouts[unique_id] = base_loadout
            original_loadouts = store.npc_loadouts
            store.npc_loadouts = temp_loadouts
            npc.apply_loadout(unique_id)
            store.npc_loadouts = original_loadouts
        
        store.dynamic_npcs[unique_id] = npc
        return unique_id, npc
    
    def generate_random_npc(npc_type="street_tough"):
        """
        Generate a random NPC based on a template with randomized attributes
        
        Parameters:
        - npc_type: Type of NPC to generate from npc_generation_templates
        
        Returns:
        - Tuple of (unique_id, npc_object)
        """
        if npc_type not in npc_generation_templates:
            return create_dynamic_npc()
        
        template = npc_generation_templates[npc_type]
        custom_data = {
            "stats": {"name": random.choice(template.get("name_pool", ["Unknown"]))},
            "description": random.choice(template.get("description_templates", ["A mysterious figure"])),
            "backstory": random.choice(template.get("backstory_templates", ["A fighter from the undercity streets"])),
            "fighting_style": random.choice(template.get("fighting_style_pool", ["Basic Fighter"]))
        }
        
        if "stat_boosts" in template:
            custom_data["stats"].update(template["stat_boosts"])
        
        custom_data["loadout"] = {"equipment": {}}
        if "equipment_variants" in template:
            custom_data["loadout"]["equipment"] = random.choice(template["equipment_variants"])
        elif "guaranteed_equipment" in template:
            custom_data["loadout"]["equipment"] = template["guaranteed_equipment"]
        
        return create_dynamic_npc(template_id=template.get("base_template"), custom_data=custom_data)
    
    def cleanup_old_dynamic_npcs(max_age_days=7):
        """
        Remove old dynamic NPCs to prevent save file bloat
        
        Parameters:
        - max_age_days: NPCs older than this many days will be removed
        """
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 60 * 60
        to_remove = [npc_id for npc_id, npc in store.dynamic_npcs.items() if hasattr(npc, 'creation_timestamp') and npc.creation_timestamp and (current_time - (float(npc.creation_timestamp) / 1000)) > max_age_seconds]
        for npc_id in to_remove:
            del store.dynamic_npcs[npc_id]
        return len(to_remove)
    
    def find_dynamic_npcs_by_name(name):
        """Find dynamic NPCs by name"""
        return {k: v for k, v in store.dynamic_npcs.items() if v.name == name}
    
    def get_dynamic_npc_info(npc_id):
        """Get detailed information about a dynamic NPC"""
        if npc_id not in store.dynamic_npcs:
            return None
        npc = store.dynamic_npcs[npc_id]
        return {
            "name": npc.name, "description": npc.description, "backstory": npc.backstory,
            "fighting_style": npc.fighting_style, "hp": npc.hp, "max_hp": npc.max_hp, "ac": npc.ac,
            "stats": {"str": npc.strength, "dex": npc.dexterity, "con": npc.constitution,
                     "int": npc.intelligence, "wis": npc.wisdom, "cha": npc.charisma},
            "equipped_items": [item.name for item in npc.equipped_items],
            "skills": npc.learned_skills, "active_skills": npc.active_skills,
            "creation_time": npc.creation_timestamp
        }

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
#     "name": "NPC Name", "hp": 20, "ac": 14, "str": 12, "dex": 12, "con": 12, 
#     "intl": 12, "wis": 12, "cha": 12
# }
#
# # Step 2: Define loadout (equipment, skills, etc)
# default npc_loadouts["new_npc_id"] = {
#     "equipment": {"weapon": "item_id_here", "armor": "item_id_here", "accessory": None, "inventory": ["item_1", "item_2"]},
#     "skills": {"skill_id_1": 2, "skill_id_2": 1},
#     "active_skills": ["skill_id_1"]
# }
#
# # Step 3: Create the NPC in initialize_npcs label
# $ npc_roster["new_npc_id"] = create_npc_with_loadout("new_npc_id")
#
# # Or create a variant with custom stats
# $ npc_roster["npc_variant"] = create_npc_with_loadout("new_npc_id", {"name": "Custom Name", "hp": 30})
#

# ----- HOW TO USE THE DYNAMIC NPC SYSTEM -----
#
# The dynamic NPC system allows you to create NPCs on-the-fly during gameplay.
# These NPCs are automatically saved and persist across game sessions.
#
# # Example 1: Create a specific custom boss enemy
# label create_boss_fight:
#     python:
#         boss_id, boss_npc = create_dynamic_npc(template_id="sevika", custom_data={
#             "stats": {"name": "The Iron Fist", "hp": 80, "str": 20, "ac": 18},
#             "description": "A massive enforcer with cybernetic implants and a reputation for brutality.",
#             "backstory": "Once a pit fighter, now Silco's personal executioner.",
#             "fighting_style": "Heavy Brawler",
#             "loadout": {
#                 "equipment": {"weapon": "sevikas_puncher", "armor": "reinforced_vest", "accessory": "chem_stimulator"},
#                 "skills": {"intimidation": 3, "tough_as_nails": 4},
#                 "active_skills": ["intimidation", "tough_as_nails"]
#             }
#         })
#
# # Example 2: Generate random enemies for a group fight
# label spawn_street_fight:
#     python:
#         enemies = [generate_random_npc("street_tough")[0] for _ in range(3)]
#
# # Example 5: Cleanup old NPCs (call periodically)
# label cleanup_npcs:
#     python:
#         cleaned_count = cleanup_old_dynamic_npcs(7)
#         if cleaned_count > 0:
#             print(f"Cleaned up {cleaned_count} old dynamic NPCs")
#
# ----- ADDING NEW NPC GENERATION TEMPLATES -----
#
# To add a new type of randomly generated NPC, add an entry to npc_generation_templates:
#
# default npc_generation_templates["new_type"] = {
#     "base_template": "template_to_use", "name_pool": ["Name1", "Name2", "Name3"],
#     "description_templates": ["Description option 1", "Description option 2"],
#     "backstory_templates": ["Backstory option 1", "Backstory option 2"],
#     "fighting_style_pool": ["Style1", "Style2"], "stat_boosts": {"hp": 5, "str": 2},
#     "equipment_variants": [{"weapon": "item1", "armor": "item2"}, {"weapon": "item3", "armor": None}],
#     "guaranteed_equipment": {"weapon": "item4"}
# }
#
# Then use: generate_random_npc("new_type")
