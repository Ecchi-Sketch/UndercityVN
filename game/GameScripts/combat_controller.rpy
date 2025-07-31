#============================================================================
# ENHANCED COMBAT CONTROLLER SYSTEM
#============================================================================
# This file contains the new combat mechanics backend that separates
# mechanical combat processing from GUI display
#============================================================================

python early:
    import random
    import time
    from collections import defaultdict

    class CombatLogEntry:
        """Stores detailed mechanical information about a single combat action"""
        def __init__(self, round_num, participant, action_type, roll_result=None, 
                     target=None, damage=None, status="", timestamp=None):
            self.round = round_num
            self.participant = participant
            self.action_type = action_type  # "attack", "defend", "cast", "move", "special"
            self.roll_result = roll_result   # {"d20": 15, "modifier": 3, "total": 18, "advantage": False}
            self.target = target
            self.damage = damage            # {"dice": "1d8+3", "rolls": [6], "modifier": 3, "total": 9, "type": "slashing"}
            self.status = status           # "hit", "miss", "critical", "fumble", "save_success", "save_fail"
            self.timestamp = timestamp or time.time()
            self.narrative_generated = False  # Flag to track if spAcy narrative was generated
            
        def format_mechanical_display(self):
            """Format this entry for the mechanical combat log display"""
            lines = []
            
            # Header line with round and action
            header = f"Round {self.round} | {self.participant.name}"
            if self.action_type == "attack" and self.target:
                header += f" attacks {self.target.name}"
            elif self.action_type == "cast":
                header += f" casts spell"
            elif self.action_type == "defend":
                header += f" defends"
            
            lines.append(header)
            
            # Roll information
            if self.roll_result:
                roll_line = f"  Roll: d20({self.roll_result.get('d20', 0)})"
                if self.roll_result.get('modifier', 0) != 0:
                    mod = self.roll_result['modifier']
                    roll_line += f" {'+' if mod >= 0 else ''}{mod}"
                roll_line += f" = {self.roll_result.get('total', 0)}"
                
                if self.action_type == "attack" and self.target:
                    roll_line += f" vs AC {getattr(self.target, 'ac', 10)} → {self.status.upper()}"
                
                if self.roll_result.get('advantage'):
                    roll_line += " (ADV)"
                elif self.roll_result.get('disadvantage'):
                    roll_line += " (DIS)"
                    
                lines.append(roll_line)
            
            # Damage information
            if self.damage and self.damage.get('total', 0) > 0:
                dmg_line = f"  Damage: {self.damage.get('dice', 'unknown')}"
                if self.damage.get('rolls'):
                    dmg_line += f"({','.join(map(str, self.damage['rolls']))})"
                if self.damage.get('modifier', 0) != 0:
                    mod = self.damage['modifier']
                    dmg_line += f" {'+' if mod >= 0 else ''}{mod}"
                dmg_line += f" = {self.damage['total']} {self.damage.get('type', 'damage')}"
                lines.append(dmg_line)
            
            return "\n".join(lines)

    class DiceRoll:
        """Handles dice rolling with advantage/disadvantage and modifiers"""
        def __init__(self, sides=20, modifier=0, advantage=False, disadvantage=False):
            self.sides = sides
            self.modifier = modifier
            self.advantage = advantage
            self.disadvantage = disadvantage
            
        def roll(self):
            """Execute the dice roll and return detailed results"""
            if self.advantage and self.disadvantage:
                # Advantage and disadvantage cancel out
                roll1 = random.randint(1, self.sides)
                return {
                    "d20": roll1,
                    "modifier": self.modifier,
                    "total": roll1 + self.modifier,
                    "advantage": False,
                    "disadvantage": False,
                    "rolls": [roll1]
                }
            elif self.advantage:
                roll1 = random.randint(1, self.sides)
                roll2 = random.randint(1, self.sides)
                best_roll = max(roll1, roll2)
                return {
                    "d20": best_roll,
                    "modifier": self.modifier,
                    "total": best_roll + self.modifier,
                    "advantage": True,
                    "disadvantage": False,
                    "rolls": [roll1, roll2],
                    "chosen_roll": best_roll
                }
            elif self.disadvantage:
                roll1 = random.randint(1, self.sides)
                roll2 = random.randint(1, self.sides)
                worst_roll = min(roll1, roll2)
                return {
                    "d20": worst_roll,
                    "modifier": self.modifier,
                    "total": worst_roll + self.modifier,
                    "advantage": False,
                    "disadvantage": True,
                    "rolls": [roll1, roll2],
                    "chosen_roll": worst_roll
                }
            else:
                roll1 = random.randint(1, self.sides)
                return {
                    "d20": roll1,
                    "modifier": self.modifier,
                    "total": roll1 + self.modifier,
                    "advantage": False,
                    "disadvantage": False,
                    "rolls": [roll1]
                }

    class DamageRoll:
        """Handles damage dice rolling"""
        def __init__(self, dice_string, modifier=0, critical=False):
            self.dice_string = dice_string  # e.g., "1d8", "2d6"
            self.modifier = modifier
            self.critical = critical
            
        def parse_dice_string(self, dice_str):
            """Parse dice string like '1d8' or '2d6' into count and sides"""
            if 'd' not in dice_str:
                return 1, int(dice_str)  # Handle single numbers
            parts = dice_str.split('d')
            count = int(parts[0]) if parts[0] else 1
            sides = int(parts[1])
            return count, sides
            
        def roll(self):
            """Execute damage roll with critical hit doubling"""
            count, sides = self.parse_dice_string(self.dice_string)
            
            # Double dice on critical hit
            if self.critical:
                count *= 2
                
            rolls = []
            for _ in range(count):
                rolls.append(random.randint(1, sides))
                
            total = sum(rolls) + self.modifier
            
            return {
                "dice": f"{count}d{sides}" + (f"+{self.modifier}" if self.modifier > 0 else f"{self.modifier}" if self.modifier < 0 else ""),
                "rolls": rolls,
                "modifier": self.modifier,
                "total": max(0, total),  # Damage can't be negative
                "critical": self.critical
            }

    class CombatController:
        """Main controller for enhanced combat mechanics"""
        def __init__(self):
            self.combat_log = []  # List of CombatLogEntry objects
            self.combat_narratives = []  # List of narrative strings
            self.current_action = None
            self.round_number = 1
            self.turn_index = 0
            self.participants = []
            
        def initialize_combat(self, participants):
            """Initialize a new combat encounter"""
            self.participants = participants[:]
            self.combat_log = []
            self.combat_narratives = []
            self.round_number = 1
            self.turn_index = 0
            
            # Roll initiative for all participants
            self.roll_initiative()
            
        def roll_initiative(self):
            """Roll initiative for all participants and sort by result"""
            initiative_rolls = []
            
            for participant in self.participants:
                # Get dexterity modifier
                dex_mod = (getattr(participant, 'dexterity', 10) - 10) // 2
                
                # Roll d20 + dex modifier
                roll = random.randint(1, 20) + dex_mod
                initiative_rolls.append((participant, roll))
                
                # Log the initiative roll
                log_entry = CombatLogEntry(
                    round_num=0,  # Initiative is round 0
                    participant=participant,
                    action_type="initiative",
                    roll_result={"d20": roll - dex_mod, "modifier": dex_mod, "total": roll},
                    status="rolled"
                )
                self.combat_log.append(log_entry)
            
            # Sort by initiative (highest first)
            initiative_rolls.sort(key=lambda x: x[1], reverse=True)
            self.participants = [p[0] for p in initiative_rolls]
            
        def get_current_participant(self):
            """Get the participant whose turn it is"""
            if self.participants:
                return self.participants[self.turn_index]
            return None
            
        def advance_turn(self):
            """Advance to the next participant's turn"""
            if not self.participants:
                return
                
            self.turn_index += 1
            if self.turn_index >= len(self.participants):
                self.turn_index = 0
                self.round_number += 1
                
        def process_attack(self, attacker, target, weapon_name="weapon", advantage=False, disadvantage=False):
            """Process a complete attack action with roll, hit determination, and damage"""
            # Calculate attack bonus
            str_mod = (getattr(attacker, 'strength', 10) - 10) // 2
            prof_bonus = getattr(attacker, 'proficiency_bonus', 2)
            weapon_bonus = getattr(attacker, 'atk_bonus', 0)
            total_attack_bonus = str_mod + prof_bonus + weapon_bonus
            
            # Roll attack
            attack_roll = DiceRoll(20, total_attack_bonus, advantage, disadvantage)
            roll_result = attack_roll.roll()
            
            # Determine hit/miss
            target_ac = getattr(target, 'ac', 10)
            natural_20 = roll_result['d20'] == 20
            natural_1 = roll_result['d20'] == 1
            
            if natural_1:
                # Critical miss
                hit = False
                critical = False
                status = "fumble"
            elif natural_20 or roll_result['total'] >= target_ac:
                # Hit (natural 20 is always a hit)
                hit = True
                # Critical hit on natural 20 OR exceeding AC by 7+
                critical = natural_20 or (roll_result['total'] - target_ac >= 7)
                status = "critical" if critical else "hit"
            else:
                # Miss
                hit = False
                critical = False
                status = "miss"
            
            # Create attack log entry
            attack_entry = CombatLogEntry(
                round_num=self.round_number,
                participant=attacker,
                action_type="attack",
                roll_result=roll_result,
                target=target,
                status=status
            )
            
            # Process damage if hit
            if hit:
                damage_result = self.process_damage(attacker, target, weapon_name, critical)
                attack_entry.damage = damage_result
                
                # Apply damage to target
                if hasattr(target, 'hp') and damage_result['total'] > 0:
                    target.hp = max(0, target.hp - damage_result['total'])
            
            # Add to combat log
            self.combat_log.append(attack_entry)
            
            return attack_entry
            
        def process_damage(self, attacker, target, weapon_name, critical=False):
            """Process damage roll for an attack"""
            # Get damage dice based on weapon or default
            if hasattr(attacker, 'equipped_items') and attacker.equipped_items:
                # Try to get weapon damage from equipped items
                damage_dice = "1d6"  # Default
            else:
                damage_dice = "1d6"  # Default damage
                
            # Calculate damage modifier
            str_mod = (getattr(attacker, 'strength', 10) - 10) // 2
            weapon_dmg_bonus = getattr(attacker, 'dmg_bonus', 0)
            total_damage_bonus = str_mod + weapon_dmg_bonus
            
            # Roll damage
            damage_roll = DamageRoll(damage_dice, total_damage_bonus, critical)
            damage_result = damage_roll.roll()
            damage_result['type'] = 'slashing'  # Default damage type
            
            return damage_result
            
        def process_spell_cast(self, caster, spell_name, target=None, spell_level=1):
            """Process a spell casting action"""
            # For now, simplified spell processing
            log_entry = CombatLogEntry(
                round_num=self.round_number,
                participant=caster,
                action_type="cast",
                target=target,
                status="cast"
            )
            
            self.combat_log.append(log_entry)
            return log_entry
            
        def get_mechanical_log_display(self, last_n_entries=10):
            """Get formatted mechanical log for display"""
            recent_entries = self.combat_log[-last_n_entries:] if last_n_entries else self.combat_log
            formatted_entries = []
            
            for entry in recent_entries:
                formatted_entries.append(entry.format_mechanical_display())
                
            return "\n\n".join(formatted_entries)
            
        def add_narrative(self, narrative_text):
            """Add a narrative description to the combat"""
            self.combat_narratives.append({
                "text": narrative_text,
                "timestamp": time.time(),
                "round": self.round_number
            })

# Initialize global combat controller
default enhanced_combat_controller = CombatController()
