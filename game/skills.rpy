#// ------------------------------------------------------------------------------------------------
#// Learned Skill Definitions
#// ------------------------------------------------------------------------------------------------
#// This file defines the classes and database for all passive skills the player can learn.
#// ------------------------------------------------------------------------------------------------
#//Learn a Skill: To give the player the "New Kid in Town" skill, you would add this line somewhere in your game script:
#//$ player_stats.learn_skill("new_kid_in_town")

#//Level Up a Skill: To increase the level of that skill, you would use:
#//$ player_stats.level_up_skill("new_kid_in_town")

#// to add xp and skill xp
#// $ player_stats.gain_xp(base_amount=50, skill_amount=10)

init python:
    # The base class for all learnable skills.
    class LearnedSkill:
        def __init__(self, id, name, description, max_level, base_effects, per_level_effects, manifestation_name, manifestation_desc):
            self.id = id
            self.name = name
            self.description = description
            self.max_level = max_level
            # A dictionary of bonuses the skill provides at level 1.
            self.base_effects = base_effects
            # A dictionary of bonuses gained for each level after the first.
            self.per_level_effects = per_level_effects
            # The special ability unlocked at max level.
            self.manifestation_name = manifestation_name
            self.manifestation_desc = manifestation_desc

    # This dictionary will hold all defined skills for easy access.
    skill_database = {}

# This label should be called once at the start of the game to populate the database.
label initialize_skills:
    python:
        skill_database["new_kid_in_town"] = LearnedSkill(
            id="new_kid_in_town",
            name="New Kid in Town",
            description="You're new to these streets, and that makes you dangerous. You've learned to be quick, tough, and to hit hard to survive.",
            max_level=10,
            base_effects={"ac_bonus": 5, "atk_bonus": 5, "dmg_bonus": 5},
            per_level_effects={"ac_bonus": 1, "atk_bonus": 1, "dmg_bonus": 1},
            manifestation_name="Local Legend",
            manifestation_desc="Your first attack in combat is a guaranteed critical hit."
        )

        skill_database["test_skill"] = LearnedSkill(
            id="test_skill",
            name="Test Skill",
            description="This is a test of the new skill input process.",
            max_level=10,
            base_effects={"ac_bonus": 5, "atk_bonus": 5, "dmg_bonus": 5},
            per_level_effects={"ac_bonus": 1, "atk_bonus": 1, "dmg_bonus": 1},
            manifestation_name="TBD Manifestation",
            manifestation_desc="You've reached the lvl 10 manifestation ability!"
        )
        
        skill_database["scavenger"] = LearnedSkill(
            id="scavenger",
            name="Scavenger",
            description="Years of surviving in the undercity have taught you to find resources where others see only trash.",
            max_level=5,
            base_effects={"ac_bonus": 1},
            per_level_effects={"ac_bonus": 1},
            manifestation_name="Wasteland Hunter",
            manifestation_desc="You can find valuable items in the most unlikely places."
        )
        
        skill_database["tough_as_nails"] = LearnedSkill(
            id="tough_as_nails",
            name="Tough as Nails",
            description="You've endured so much pain that your body has adapted to withstand punishment that would fell others.",
            max_level=5,
            base_effects={"max_hp_percent_bonus": 0.1},  # 10% more HP
            per_level_effects={"max_hp_percent_bonus": 0.05},  # +5% per level
            manifestation_name="Unbreakable",
            manifestation_desc="You become immune to being knocked unconscious by non-lethal damage."
        )
        
        skill_database["street_fighter"] = LearnedSkill(
            id="street_fighter",
            name="Street Fighter",
            description="You've learned to fight dirty in the undercity's brutal conflicts, using every advantage to survive.",
            max_level=5,
            base_effects={"atk_bonus": 2, "dmg_bonus": 1},
            per_level_effects={"atk_bonus": 1, "dmg_bonus": 1},
            manifestation_name="Dirty Fighter",
            manifestation_desc="Your critical hits have a chance to inflict debilitating status effects."
        )
        
        skill_database["intimidation"] = LearnedSkill(
            id="intimidation",
            name="Intimidation",
            description="Your presence alone can make enemies think twice about fighting you.",
            max_level=3,
            base_effects={"ac_bonus": 1},  # Enemies hesitate to attack
            per_level_effects={"ac_bonus": 1},
            manifestation_name="Terrifying Presence",
            manifestation_desc="Enemies must make a morale check or flee when they see you."
        )
        
        skill_database["dodge"] = LearnedSkill(
            id="dodge",
            name="Dodge",
            description="You've mastered the art of evasion, making your opponents struggle to land clean hits.",
            max_level=3,
            base_effects={},  # No passive effects - this is an active skill
            per_level_effects={},
            manifestation_name="Untouchable",
            manifestation_desc="When you dodge, you can immediately counterattack with advantage."
        )
        
        skill_database["block"] = LearnedSkill(
            id="block",
            name="Block",
            description="You can raise your guard to reduce incoming damage through defensive positioning.",
            max_level=5,
            base_effects={},  # No passive effects - this is an active skill
            per_level_effects={},
            manifestation_name="Immovable Defense",
            manifestation_desc="Your blocks can completely negate attacks and reflect damage back to attackers."
        )
    return
