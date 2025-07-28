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
    return
