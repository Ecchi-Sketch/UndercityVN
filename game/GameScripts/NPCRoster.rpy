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
            "weapon": "sevikas_puncher",
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
        npc = CharacterStats(**base_stats)
        
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
    def create_dynamic_npc(template_id=None, custom_data=None):
        """
        Create a dynamic NPC for battle situations or story encounters
        
        Parameters:
        - template_id: Base template to use (e.g., "zaunite_thug_template")
        - custom_data: Dictionary with custom overrides for stats, description, etc.
        
        Returns:
        - Tuple of (unique_id, npc_object) - The NPC is automatically stored in dynamic_npcs
        
        Example usage:
        boss_id, boss_npc = create_dynamic_npc(
            template_id="sevika",
            custom_data={
                "stats": {"name": "The Iron Fist", "hp": 80, "str": 20},
                "description": "A massive enforcer with cybernetic implants",
                "backstory": "Once a pit fighter, now Silco's executioner",
                "fighting_style": "Heavy Brawler",
                "loadout": {
                    "equipment": {"weapon": "sevikas_puncher", "armor": "reinforced_vest"},
                    "skills": {"intimidation": 3, "tough_as_nails": 4}
                }
            }
        )
        """
        import time
        
        # Generate unique ID for this NPC
        timestamp = str(int(time.time() * 1000))  # Include milliseconds for uniqueness
        unique_id = f"dynamic_npc_{timestamp}"
        
        # Start with template or default stats
        if template_id and template_id in default_npc_stats:
            base_stats = default_npc_stats[template_id].copy()
            base_loadout = npc_loadouts.get(template_id, {}).copy() if template_id in npc_loadouts else {}
        else:
            # Default generic NPC stats
            base_stats = {
                "name": "Unknown Fighter",
                "hp": 15, "ac": 12, "str": 12, "dex": 12, "con": 12,
                "intl": 10, "wis": 10, "cha": 10
            }
            base_loadout = {
                "equipment": {"weapon": "makeshift_shiv", "armor": None, "accessory": None, "inventory": []},
                "skills": {},
                "active_skills": []
            }
        
        # Apply custom overrides
        if custom_data:
            # Update base stats
            if "stats" in custom_data:
                base_stats.update(custom_data["stats"])
                
            # Merge equipment loadout
            if "loadout" in custom_data:
                custom_loadout = custom_data["loadout"]
                if "equipment" in custom_loadout:
                    if "equipment" not in base_loadout:
                        base_loadout["equipment"] = {}
                    base_loadout["equipment"].update(custom_loadout["equipment"])
                if "skills" in custom_loadout:
                    if "skills" not in base_loadout:
                        base_loadout["skills"] = {}
                    base_loadout["skills"].update(custom_loadout["skills"])
                if "active_skills" in custom_loadout:
                    base_loadout["active_skills"] = custom_loadout["active_skills"]
        
        # Create the NPC with extended fields
        npc = CharacterStats(
            name=base_stats.get("name", "Unknown Fighter"),
            hp=base_stats.get("hp", 15),
            ac=base_stats.get("ac", 12),
            str=base_stats.get("str", 12),
            dex=base_stats.get("dex", 12),
            con=base_stats.get("con", 12),
            intl=base_stats.get("intl", 10),
            wis=base_stats.get("wis", 10),
            cha=base_stats.get("cha", 10),
            description=custom_data.get("description", "") if custom_data else "",
            backstory=custom_data.get("backstory", "") if custom_data else "",
            fighting_style=custom_data.get("fighting_style", "") if custom_data else ""
        )
        
        # Mark as dynamic and set creation time
        npc.is_dynamic = True
        npc.creation_timestamp = timestamp
        
        # Apply loadout by temporarily adding to npc_loadouts
        if base_loadout:
            temp_loadouts = npc_loadouts.copy()
            temp_loadouts[unique_id] = base_loadout
            
            # Store original and update
            original_loadouts = store.npc_loadouts
            store.npc_loadouts = temp_loadouts
            
            # Apply the loadout
            npc.apply_loadout(unique_id)
            
            # Restore original loadouts
            store.npc_loadouts = original_loadouts
        
        # Store in dynamic NPCs registry
        store.dynamic_npcs[unique_id] = npc
        
        return unique_id, npc
    
    def generate_random_npc(npc_type="street_tough"):
        """
        Generate a random NPC based on a template with randomized attributes
        
        Parameters:
        - npc_type: Type of NPC to generate from npc_generation_templates
        
        Returns:
        - Tuple of (unique_id, npc_object)
        
        Example usage:
        # Generate a random street tough
        enemy_id, enemy_npc = generate_random_npc("street_tough")
        
        # Generate multiple enemies for a fight
        enemies = []
        for i in range(3):
            enemy_id, enemy_npc = generate_random_npc("street_tough")
            enemies.append(enemy_id)
        """
        import random
        
        if npc_type not in npc_generation_templates:
            return create_dynamic_npc()
        
        template = npc_generation_templates[npc_type]
        
        # Generate random attributes
        custom_data = {
            "stats": {
                "name": random.choice(template.get("name_pool", ["Unknown"]))
            },
            "description": random.choice(template.get("description_templates", ["A mysterious figure"])),
            "backstory": random.choice(template.get("backstory_templates", ["A fighter from the undercity streets"])),
            "fighting_style": random.choice(template.get("fighting_style_pool", ["Basic Fighter"]))
        }
        
        # Apply stat boosts if defined
        if "stat_boosts" in template:
            custom_data["stats"].update(template["stat_boosts"])
        
        # Apply equipment
        custom_data["loadout"] = {"equipment": {}}
        if "equipment_variants" in template:
            equipment = random.choice(template["equipment_variants"])
            custom_data["loadout"]["equipment"] = equipment
        elif "guaranteed_equipment" in template:
            custom_data["loadout"]["equipment"] = template["guaranteed_equipment"]
        
        return create_dynamic_npc(
            template_id=template.get("base_template"),
            custom_data=custom_data
        )
    
    def cleanup_old_dynamic_npcs(max_age_days=7):
        """
        Remove old dynamic NPCs to prevent save file bloat
        
        Parameters:
        - max_age_days: NPCs older than this many days will be removed
        
        Example usage:
        # Clean up NPCs older than 3 days
        cleanup_old_dynamic_npcs(3)
        """
        import time
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 60 * 60
        
        to_remove = []
        for npc_id, npc in store.dynamic_npcs.items():
            if hasattr(npc, 'creation_timestamp') and npc.creation_timestamp:
                npc_age = current_time - (float(npc.creation_timestamp) / 1000)  # Convert from milliseconds
                if npc_age > max_age_seconds:
                    to_remove.append(npc_id)
        
        for npc_id in to_remove:
            del store.dynamic_npcs[npc_id]
        
        return len(to_remove)  # Return number of NPCs cleaned up
    
    def find_dynamic_npcs_by_name(name):
        """
        Find dynamic NPCs by name
        
        Parameters:
        - name: Name to search for
        
        Returns:
        - Dictionary of {npc_id: npc_object} matching the name
        
        Example usage:
        # Find all NPCs named "Razor"
        razors = find_dynamic_npcs_by_name("Razor")
        for npc_id, npc in razors.items():
            # Do something with each Razor
        """
        return {k: v for k, v in store.dynamic_npcs.items() if v.name == name}
    
    def get_dynamic_npc_info(npc_id):
        """
        Get detailed information about a dynamic NPC
        
        Parameters:
        - npc_id: ID of the dynamic NPC
        
        Returns:
        - Dictionary with NPC information or None if not found
        """
        if npc_id not in store.dynamic_npcs:
            return None
            
        npc = store.dynamic_npcs[npc_id]
        return {
            "name": npc.name,
            "description": npc.description,
            "backstory": npc.backstory,
            "fighting_style": npc.fighting_style,
            "hp": npc.hp,
            "max_hp": npc.max_hp,
            "ac": npc.ac,
            "stats": {"str": npc.strength, "dex": npc.dexterity, "con": npc.constitution,
                     "int": npc.intelligence, "wis": npc.wisdom, "cha": npc.charisma},
            "equipped_items": [item.name for item in npc.equipped_items],
            "skills": npc.learned_skills,
            "active_skills": npc.active_skills,
            "creation_time": npc.creation_timestamp
        }

# ----- HOW TO USE THE DYNAMIC NPC SYSTEM -----
#
# The dynamic NPC system allows you to create NPCs on-the-fly during gameplay.
# These NPCs are automatically saved and persist across game sessions.
#
# ----- BASIC USAGE EXAMPLES -----
#
# # Example 1: Create a specific custom boss enemy
# label create_boss_fight:
#     python:
#         boss_id, boss_npc = create_dynamic_npc(
#             template_id="sevika",
#             custom_data={
#                 "stats": {
#                     "name": "The Iron Fist",
#                     "hp": 80,
#                     "str": 20,
#                     "ac": 18
#                 },
#                 "description": "A massive enforcer with cybernetic implants and a reputation for brutality.",
#                 "backstory": "Once a pit fighter, now Silco's personal executioner.",
#                 "fighting_style": "Heavy Brawler",
#                 "loadout": {
#                     "equipment": {
#                         "weapon": "sevikas_puncher",
#                         "armor": "reinforced_vest",
#                         "accessory": "chem_stimulator"
#                     },
#                     "skills": {"intimidation": 3, "tough_as_nails": 4},
#                     "active_skills": ["intimidation", "tough_as_nails"]
#                 }
#             }
#         )
#         
#         # Boss is now available as dynamic_npcs[boss_id]
#         # Use boss_npc for combat or dialogue
#
# # Example 2: Generate random enemies for a group fight
# label spawn_street_fight:
#     python:
#         enemies = []
#         for i in range(3):
#             enemy_id, enemy_npc = generate_random_npc("street_tough")
#             enemies.append(enemy_id)
#         
#         # Now you have 3 random street toughs ready for combat
#         # Access them via dynamic_npcs[enemy_id]
#
# # Example 3: Create a unique NPC without a template
# label create_unique_character:
#     python:
#         unique_id, unique_npc = create_dynamic_npc(
#             custom_data={
#                 "stats": {
#                     "name": "Mysterious Stranger",
#                     "hp": 25,
#                     "ac": 15,
#                     "str": 14, "dex": 16, "con": 13,
#                     "intl": 15, "wis": 14, "cha": 12
#                 },
#                 "description": "A hooded figure whose face is hidden in shadow.",
#                 "backstory": "Their past is shrouded in mystery.",
#                 "fighting_style": "Unknown",
#                 "loadout": {
#                     "equipment": {
#                         "weapon": "advanced_shiv",
#                         "armor": None,
#                         "accessory": None,
#                         "inventory": ["healing_draught"]
#                     }
#                 }
#             }
#         )
#
# # Example 4: Using dynamic NPCs in dialogue or combat
# label encounter_dynamic_npc:
#     python:
#         # Assume we stored an enemy_id from earlier
#         if "my_enemy_id" in globals() and my_enemy_id in dynamic_npcs:
#             enemy = dynamic_npcs[my_enemy_id]
#             enemy_name = enemy.name
#             enemy_desc = enemy.description
#     
#     "You face [enemy_name]."
#     "[enemy_desc]"
#     
#     menu:
#         "Fight":
#             # Use enemy in combat system
#             pass
#         "Talk":
#             # Use enemy.backstory or other info in dialogue
#             pass
#
# # Example 5: Cleanup old NPCs (call periodically)
# label cleanup_npcs:
#     python:
#         cleaned_count = cleanup_old_dynamic_npcs(7)  # Remove NPCs older than 7 days
#         if cleaned_count > 0:
#             print(f"Cleaned up {cleaned_count} old dynamic NPCs")
#
# ----- ADDING NEW NPC GENERATION TEMPLATES -----
#
# To add a new type of randomly generated NPC, add an entry to npc_generation_templates:
#
# default npc_generation_templates["new_type"] = {
#     "base_template": "template_to_use",  # Optional: base from existing NPC
#     "name_pool": ["Name1", "Name2", "Name3"],  # Random names
#     "description_templates": [  # Random descriptions
#         "Description option 1",
#         "Description option 2"
#     ],
#     "backstory_templates": [  # Random backstories
#         "Backstory option 1",
#         "Backstory option 2"
#     ],
#     "fighting_style_pool": ["Style1", "Style2"],  # Random fighting styles
#     "stat_boosts": {"hp": 5, "str": 2},  # Optional: stat modifications
#     "equipment_variants": [  # Optional: random equipment sets
#         {"weapon": "item1", "armor": "item2"},
#         {"weapon": "item3", "armor": None}
#     ],
#     "guaranteed_equipment": {"weapon": "item4"}  # Alternative: fixed equipment
# }
#
# Then use: generate_random_npc("new_type")
#
