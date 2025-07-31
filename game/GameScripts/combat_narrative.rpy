#============================================================================
# SPACY-POWERED COMBAT NARRATIVE GENERATION SYSTEM
#============================================================================
# This file contains the narrative generation system that creates rich,
# contextual descriptions of combat actions using natural language processing
#============================================================================

python early:
    import random
    
    class CombatNarrativeGenerator:
        """Generates rich narrative descriptions of combat actions"""
        
        def __init__(self):
            # For now, we'll use template-based generation with contextual awareness
            # In the future, this could be enhanced with actual spAcy integration
            self.spacy_nlp = None  # Placeholder for spAcy model
            
            # Weapon-specific attack descriptions
            self.weapon_attacks = {
                "sword": [
                    "slashes with {weapon}",
                    "brings {weapon} down in a powerful arc",
                    "thrusts {weapon} forward with precision",
                    "whirls {weapon} in a deadly dance"
                ],
                "dagger": [
                    "strikes quickly with {weapon}",
                    "darts in with {weapon} gleaming",
                    "flicks {weapon} toward vital spots",
                    "weaves through defenses with {weapon}"
                ],
                "axe": [
                    "swings {weapon} with devastating force",
                    "brings {weapon} around in a crushing blow",
                    "hefts {weapon} and strikes downward",
                    "cleaves the air with {weapon}"
                ],
                "mace": [
                    "pounds forward with {weapon}",
                    "brings {weapon} crashing down",
                    "swings {weapon} in a bone-crushing arc",
                    "hammers at the enemy with {weapon}"
                ],
                "staff": [
                    "strikes with {weapon}",
                    "spins {weapon} in practiced movements",
                    "thrusts {weapon} like a spear",
                    "sweeps {weapon} in a wide arc"
                ],
                "default": [
                    "attacks with fierce determination",
                    "strikes with practiced skill",
                    "moves with deadly intent",
                    "launches a calculated assault"
                ]
            }
            
            # Hit result descriptions
            self.hit_results = {
                "critical": [
                    "The strike finds its mark perfectly, {damage_desc}",
                    "A devastating blow connects, {damage_desc}",
                    "The attack strikes true with exceptional force, {damage_desc}",
                    "A masterful strike hits exactly where intended, {damage_desc}"
                ],
                "hit": [
                    "The attack connects, {damage_desc}",
                    "The strike finds its target, {damage_desc}",
                    "The blow lands solidly, {damage_desc}",
                    "The weapon strikes home, {damage_desc}"
                ],
                "miss": [
                    "but {target_name} {dodge_action}",
                    "but the strike goes wide",
                    "but {target_name} deflects the blow",
                    "but the attack fails to connect"
                ],
                "fumble": [
                    "but stumbles in the attempt",
                    "but loses balance during the attack",
                    "but the weapon slips in {attacker_pronoun} grip",
                    "but overextends and leaves {attacker_pronoun}self exposed"
                ]
            }
            
            # Dodge actions for misses
            self.dodge_actions = [
                "sidesteps gracefully",
                "ducks under the swing",
                "weaves away from danger",
                "steps back just in time",
                "twists out of the way",
                "deflects with quick reflexes"
            ]
            
            # Damage descriptions based on damage amount
            self.damage_descriptions = {
                "light": [
                    "leaving a shallow cut",
                    "creating a minor wound",
                    "causing a glancing blow",
                    "inflicting a superficial injury"
                ],
                "moderate": [
                    "tearing through flesh and muscle",
                    "opening a significant wound",
                    "causing substantial injury",
                    "leaving a deep gash"
                ],
                "heavy": [
                    "rending flesh and bone",
                    "creating a grievous wound",
                    "causing devastating damage",
                    "nearly felling the target"
                ],
                "massive": [
                    "delivering a potentially fatal blow",
                    "causing catastrophic injury",
                    "striking with bone-shattering force",
                    "leaving the target reeling from the impact"
                ]
            }
            
            # Environmental context additions
            self.environmental_context = {
                "docks": [
                    "The salt air carries the sound of steel",
                    "Footsteps echo off wet wooden planks",
                    "The fog swirls around the combatants"
                ],
                "alley": [
                    "Shadows dance in the narrow passage",
                    "The walls echo with the clash of combat",
                    "Dust kicks up from the cobblestones"
                ],
                "tavern": [
                    "Patrons scatter as the fight erupts",
                    "Tables and chairs are knocked aside",
                    "The flickering candlelight illuminates the struggle"
                ],
                "default": [
                    "The air crackles with tension",
                    "Time seems to slow in the heat of battle",
                    "The combatants circle each other warily"
                ]
            }
        
        def get_weapon_type(self, weapon_name):
            """Determine weapon type from weapon name"""
            if not weapon_name:
                return "default"
                
            weapon_lower = weapon_name.lower()
            if "sword" in weapon_lower or "blade" in weapon_lower:
                return "sword"
            elif "dagger" in weapon_lower or "knife" in weapon_lower:
                return "dagger"
            elif "axe" in weapon_lower:
                return "axe"
            elif "mace" in weapon_lower or "hammer" in weapon_lower:
                return "mace"
            elif "staff" in weapon_lower or "rod" in weapon_lower:
                return "staff"
            else:
                return "default"
        
        def get_damage_category(self, damage_amount, target_max_hp):
            """Categorize damage amount relative to target's max HP"""
            if target_max_hp <= 0:
                return "light"
                
            damage_ratio = damage_amount / target_max_hp
            
            if damage_ratio <= 0.1:
                return "light"
            elif damage_ratio <= 0.25:
                return "moderate"
            elif damage_ratio <= 0.5:
                return "heavy"
            else:
                return "massive"
        
        def get_pronoun(self, character, subject=True):
            """Get appropriate pronoun for character"""
            # This could be enhanced to check character gender attributes
            # For now, use neutral pronouns
            if subject:
                return "they"
            else:
                return "them"
        
        def generate_attack_narrative(self, attacker, target, roll_data, hit_result, damage_data=None, weapon_name=None, environment="default"):
            """Generate a complete narrative description of an attack"""
            
            # Get weapon type and attack description
            weapon_type = self.get_weapon_type(weapon_name)
            attack_desc = random.choice(self.weapon_attacks[weapon_type])
            
            # Format weapon name in attack description
            if weapon_name and "{weapon}" in attack_desc:
                attack_desc = attack_desc.format(weapon=weapon_name)
            elif "{weapon}" in attack_desc:
                attack_desc = attack_desc.replace(" with {weapon}", "")
            
            # Start building the narrative
            narrative_parts = []
            
            # Opening: "[Attacker] [attack_action]"
            opening = f"{attacker.name} {attack_desc}"
            
            # Handle the result
            if hit_result == "critical" or hit_result == "hit":
                # Hit - add damage description
                if damage_data and damage_data.get('total', 0) > 0:
                    target_max_hp = getattr(target, 'max_hp', 20)
                    damage_category = self.get_damage_category(damage_data['total'], target_max_hp)
                    damage_desc = random.choice(self.damage_descriptions[damage_category])
                    
                    result_template = random.choice(self.hit_results[hit_result])
                    result_desc = result_template.format(damage_desc=damage_desc)
                    
                    narrative_parts.append(f"{opening}. {result_desc}.")
                else:
                    # Hit but no damage (shouldn't happen, but handle gracefully)
                    narrative_parts.append(f"{opening} and connects.")
                    
            elif hit_result == "miss":
                # Miss - add dodge/deflection description
                dodge_action = random.choice(self.dodge_actions)
                miss_template = random.choice(self.hit_results["miss"])
                miss_desc = miss_template.format(
                    target_name=target.name,
                    dodge_action=dodge_action
                )
                
                narrative_parts.append(f"{opening}, {miss_desc}.")
                
            elif hit_result == "fumble":
                # Critical failure
                fumble_desc = random.choice(self.hit_results["fumble"])
                attacker_pronoun = self.get_pronoun(attacker, subject=False)
                fumble_desc = fumble_desc.format(attacker_pronoun=attacker_pronoun)
                
                narrative_parts.append(f"{opening}, {fumble_desc}.")
            
            # Add environmental context occasionally (20% chance)
            if random.random() < 0.2:
                env_context = random.choice(self.environmental_context.get(environment, self.environmental_context["default"]))
                narrative_parts.append(env_context + ".")
            
            return " ".join(narrative_parts)
        
        def generate_spell_narrative(self, caster, spell_name, target=None, spell_result="success"):
            """Generate narrative for spell casting"""
            
            spell_actions = [
                f"weaves arcane energies",
                f"channels mystical power",
                f"speaks words of power",
                f"gestures with practiced precision"
            ]
            
            action = random.choice(spell_actions)
            
            if target:
                narrative = f"{caster.name} {action} and casts {spell_name} at {target.name}."
            else:
                narrative = f"{caster.name} {action} and casts {spell_name}."
            
            # Add spell effect description based on result
            if spell_result == "success":
                effects = [
                    "The magical energy crackles through the air.",
                    "Mystical forces bend to the caster's will.",
                    "The spell takes hold with visible effect."
                ]
                narrative += " " + random.choice(effects)
            
            return narrative
        
        def generate_defense_narrative(self, defender, defense_type="dodge"):
            """Generate narrative for defensive actions"""
            
            if defense_type == "dodge":
                actions = [
                    f"takes a defensive stance",
                    f"weaves through the battlefield",
                    f"focuses on evasive maneuvers",
                    f"prepares to avoid incoming attacks"
                ]
            elif defense_type == "block":
                actions = [
                    f"raises their guard",
                    f"prepares to deflect attacks",
                    f"takes a defensive posture",
                    f"readies their defense"
                ]
            else:
                actions = [
                    f"takes a cautious approach",
                    f"maintains a defensive position"
                ]
            
            action = random.choice(actions)
            return f"{defender.name} {action}."
        
        def generate_round_transition_narrative(self, round_number):
            """Generate narrative for round transitions"""
            transitions = [
                f"The battle intensifies as round {round_number} begins.",
                f"Combat continues into round {round_number}.",
                f"The fighters circle each other as round {round_number} commences.",
                f"Round {round_number} opens with renewed determination."
            ]
            
            return random.choice(transitions)
        
        def generate_combat_end_narrative(self, victor=None, result_type="victory"):
            """Generate narrative for combat conclusion"""
            if result_type == "victory" and victor:
                endings = [
                    f"{victor.name} stands victorious as the dust settles.",
                    f"The battle concludes with {victor.name} emerging triumphant.",
                    f"{victor.name} has proven superior in combat.",
                    f"Victory belongs to {victor.name} as the fighting ends."
                ]
                return random.choice(endings)
            elif result_type == "retreat":
                return "The combat ends as one side retreats from the battlefield."
            elif result_type == "draw":
                return "The combatants separate, neither claiming victory."
            else:
                return "The battle comes to an end."

# Initialize global narrative generator
default combat_narrative_generator = CombatNarrativeGenerator()
