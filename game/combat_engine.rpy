# GameScripts/combat_engine.rpy

python early:
    import re

    def get_ability_modifier(score):
        return (score - 10) // 2

    def roll_dice(dice_string):
        if not isinstance(dice_string, str):
            return int(dice_string)
        parts = re.match(r'(\d+)d(\d+)(?:\s*([+-])\s*(\d+))?', dice_string)
        if not parts:
            try: return int(dice_string)
            except ValueError: raise ValueError("Invalid dice string format: {}".format(dice_string))
        num_dice, die_size = int(parts.group(1)), int(parts.group(2))
        operator, modifier = parts.group(3), int(parts.group(4)) if parts.group(4) else 0
        total = sum(renpy.random.randint(1, die_size) for _ in range(num_dice))
        if operator == '+': total += modifier
        elif operator == '-': total -= modifier
        return total

    class Combatant:
        def __init__(self, character_obj, difficulty='N'):
            self.character_data = character_obj
            self.id = character_obj.name + "_" + str(renpy.random.randint(1000, 9999))
            self.initiative = 0
            self.current_hp = character_obj.max_hp
            self.status_effects = []
            self.action_taken, self.bonus_action_taken, self.reaction_taken = False, False, False
            self.grit_points = getattr(character_obj, 'grit_points', 1)
            if "Elite" in character_obj.name or "Enforcer" in character_obj.name or "Sevika" in character_obj.name:
                self.difficulty = 'H'
            else:
                self.difficulty = 'N'
            self.is_finished = False

        def take_damage(self, amount):
            self.current_hp = max(0, self.current_hp - amount)
        def is_defeated(self): return self.current_hp <= 0
        def get_ac(self): return self.character_data.ac
        def get_name(self): return self.character_data.name
        def reset_turn_actions(self): self.action_taken, self.bonus_action_taken, self.reaction_taken = False, False, False

    class CombatController:
        def __init__(self, narrative_generator):
            self.narrative_generator = narrative_generator
            self.participants, self.turn_order, self.mechanical_log, self.narrative_log = [], [], [], []
            self.current_turn_index, self.round_number = 0, 1
            self.combat_state, self.pending_finishing_blow = 'setup', None
            self.pending_action = None
            self.pending_initiative_rolls = []  # Track who still needs to roll initiative
            self.player_initiative_rolled = False

        def initialize_combat(self, character_objects):
            if not character_objects: return
            self.participants = [Combatant(char) for char in character_objects]
            
            # Initialize NPC initiative automatically
            for combatant in self.participants:
                if not getattr(combatant.character_data, 'is_player', False):
                    dex_mod = get_ability_modifier(combatant.character_data.dexterity)
                    combatant.initiative = renpy.random.randint(1, 20) + dex_mod
                else:
                    # Player needs to roll initiative manually
                    combatant.initiative = 0  # Placeholder
                    self.pending_initiative_rolls.append(combatant)
            
            # Check if player needs to roll initiative
            if self.pending_initiative_rolls:
                self.combat_state = 'awaiting_initiative_roll'
                self._log_event({"event_type": "initiative_prompt", "message": "Roll for initiative! (d20 + Dex modifier)"})
            else:
                self._finalize_initiative_and_start_combat()

        def get_current_combatant(self):
            if not self.turn_order: return None
            return self.turn_order[self.current_turn_index]

        def advance_turn(self):
            if self.combat_state != 'active': return
            if self._check_combat_end(): return
            self.current_turn_index = (self.current_turn_index + 1) % len(self.turn_order)
            if self.current_turn_index == 0:
                self.round_number += 1
                self._log_event({"event_type": "round_start", "round_number": self.round_number})
            if self.turn_order:
                current_combatant = self.get_current_combatant()
                current_combatant.reset_turn_actions()
                if current_combatant.is_defeated():
                    self.advance_turn()
                else:
                    self._process_npc_turn_if_applicable()

        def _process_npc_turn_if_applicable(self):
            current_combatant = self.get_current_combatant()
            if not current_combatant or getattr(current_combatant.character_data, 'is_player', False):
                return

            player_target = next((p for p in self.participants if getattr(p.character_data, 'is_player', False) and not p.is_defeated()), None)
            if player_target:
                npc_weapon = next((item for item in current_combatant.character_data.equipped_items if item.slot == 'weapon'), None)
                if npc_weapon:
                    d20_roll = renpy.random.randint(1, 20)
                    self.resolve_npc_attack(current_combatant, player_target, npc_weapon, d20_roll)
            
            if self.combat_state == 'active':
                renpy.timeout(0.5)
                self.advance_turn()

        def _log_event(self, event):
            self.mechanical_log.append(event)
            if self.narrative_generator and event.get("event_type") not in ["initiative_prompt", "initiative_roll"]:
                prose = self.narrative_generator.generate_event_prose(event)
                if prose:
                    self.narrative_log.append(prose)
            renpy.restart_interaction()

        #======================================================================
        # MODIFIED FUNCTION
        #======================================================================
        def resolve_attack(self, actor, target, weapon, total_attack_roll, roll_type=None):
            """
            Resolves the attack using the total provided by the player,
            and accounts for special roll types like Nat 20 or Nat 1.
            """
            if not all((actor, target, weapon)): return

            target_ac = target.get_ac()
            
            is_critical_hit = False
            is_critical_fumble = False
            raw_roll_display = "N/A"

            if roll_type == "nat20":
                is_critical_hit = True
                is_critical_fumble = False
                hit = True
                raw_roll_display = "Nat 20"
            elif roll_type == "nat1":
                is_critical_hit = False
                is_critical_fumble = True
                hit = False
                raw_roll_display = "Nat 1"
            else: # Standard roll logic
                is_critical_hit = (total_attack_roll - target_ac >= 7)
                is_critical_fumble = False
                hit = (is_critical_hit or total_attack_roll >= target_ac)

            # FIXED: Added full actor, target, and weapon objects to the event dictionary
            # This ensures the narrative generator receives the objects it needs, preventing the crash.
            event = {
                "event_type": "attack_resolution", 
                "actor": actor,
                "target": target,
                "weapon": weapon,
                "actor_name": actor.get_name(), 
                "target_name": target.get_name(), 
                "weapon_name": weapon.name, 
                "d20_roll": raw_roll_display, 
                "total_attack_roll": total_attack_roll, 
                "target_ac": target_ac, 
                "hit": hit, 
                "is_critical_hit": is_critical_hit, 
                "is_critical_fumble": is_critical_fumble
            }
            self._log_event(event)
            actor.action_taken = True
            
            if hit:
                self.combat_state = 'awaiting_damage_roll'
                self.pending_action['is_critical'] = is_critical_hit
                self._log_event({"event_type": "prompt_damage", "message": "HIT! Enter your total damage."})
            else:
                self.pending_action = None
                self.combat_state = 'active'
                self.advance_turn()

        def resolve_damage(self, actor, target, weapon, total_damage, is_critical):
            final_damage_to_apply = max(1, total_damage)
            target.take_damage(final_damage_to_apply)
            
            # FIXED: Added actor and target objects to the damage event so the narrative
            # generator can describe the wound severity correctly.
            event = {
                "event_type": "damage_resolution", 
                "actor": actor,
                "target": target,
                "actor_name": actor.get_name(), 
                "target_name": target.get_name(), 
                "total_damage": final_damage_to_apply, 
                "target_hp_remaining": target.current_hp, 
                "target_is_defeated": target.is_defeated()
            }
            self._log_event(event)

            if target.is_defeated() and not target.is_finished:
                self.combat_state = 'awaiting_finishing_blow'
                self.pending_finishing_blow = {"actor": actor, "target": target}
                self._log_event({"event_type": "prompt_finishing_blow", "target_name": target.get_name()})
            else:
                self.combat_state = 'active'
                self.advance_turn()
        
        def resolve_npc_attack(self, actor, target, weapon, d20_roll):
            str_mod = get_ability_modifier(actor.character_data.strength)
            atk_bonus = actor.character_data.atk_bonus
            prof_bonus = actor.character_data.proficiency_bonus
            total_attack_roll = d20_roll + str_mod + prof_bonus + atk_bonus
            target_ac = target.get_ac()
            is_critical_hit = (d20_roll == 20) or (total_attack_roll - target_ac >= 7)
            is_critical_fumble = (d20_roll == 1)
            hit = not is_critical_fumble and (is_critical_hit or total_attack_roll >= target_ac)

            # FIXED: Added full objects to the event dictionary for NPCs as well.
            attack_event = {
                "event_type": "attack_resolution", 
                "actor": actor,
                "target": target,
                "weapon": weapon,
                "actor_name": actor.get_name(), 
                "target_name": target.get_name(), 
                "weapon_name": weapon.name, 
                "d20_roll": d20_roll, 
                "total_attack_roll": total_attack_roll, 
                "target_ac": target_ac, 
                "hit": hit, 
                "is_critical_hit": is_critical_hit, 
                "is_critical_fumble": is_critical_fumble, 
                "str_mod": str_mod, 
                "prof_bonus": prof_bonus, 
                "atk_bonus": atk_bonus
            }
            self._log_event(attack_event)
            actor.action_taken = True

            if hit:
                damage_dice = weapon.effects.get("damage", "1d4")
                if is_critical_hit:
                    try:
                        num_dice = int(damage_dice.split('d')[0]) * 2
                        damage_dice = "{}d{}".format(num_dice, damage_dice.split('d')[1])
                    except: pass
                damage_roll = roll_dice(damage_dice)
                total_damage = max(1, damage_roll + str_mod + actor.character_data.dmg_bonus)
                target.take_damage(total_damage)

                # FIXED: Added full objects here too.
                damage_event = {
                    "event_type": "damage_resolution", 
                    "actor": actor,
                    "target": target,
                    "actor_name": actor.get_name(), 
                    "target_name": target.get_name(), 
                    "total_damage": total_damage, 
                    "target_hp_remaining": target.current_hp, 
                    "target_is_defeated": target.is_defeated()
                }
                self._log_event(damage_event)

                if target.is_defeated() and not target.is_finished:
                    self.resolve_finishing_blow("nonlethal", npc_actor=actor)

        def resolve_finishing_blow(self, choice, npc_actor=None):
            actor_combatant = npc_actor if npc_actor else self.pending_finishing_blow["actor"]
            target_combatant = self.pending_finishing_blow["target"] if not npc_actor else next((p for p in self.participants if p.is_defeated() and not p.is_finished), None)
            if not actor_combatant or not target_combatant: return
            target_combatant.is_finished = True
            
            weapon_name = None
            # Use character_data to access equipped_items
            if hasattr(actor_combatant.character_data, 'equipped_items') and actor_combatant.character_data.equipped_items:
                for item in actor_combatant.character_data.equipped_items:
                    if hasattr(item, 'slot') and item.slot == 'weapon':
                        weapon_name = item.name
                        break
            
            prose = self.narrative_generator.generate_finishing_blow_prose(
                actor_combatant.get_name(), 
                target_combatant.get_name(), 
                choice, 
                weapon_name=weapon_name, 
                location="underground_fight_club"
            )
            if prose: self.narrative_log.append(prose)
            self._log_event({"event_type": "finishing_blow_resolution", "actor_name": actor_combatant.get_name(), "target_name": target_combatant.get_name(), "choice": choice})
            self.pending_finishing_blow = None
            self.combat_state = 'active'
            if not npc_actor:
                self.advance_turn()

        def _check_combat_end(self):
            player_side_defeated = all(p.is_defeated() for p in self.participants if getattr(p.character_data, 'is_player', False))
            enemy_side_defeated = all(p.is_defeated() for p in self.participants if not getattr(p.character_data, 'is_player', False))
            if player_side_defeated or enemy_side_defeated:
                self.conclude_combat(victory=enemy_side_defeated)
                return True
            return False

        def conclude_combat(self, victory):
            self.combat_state = 'ended'
            total_xp, total_skill_xp, total_cc = 0, 0, 0
            if victory:
                for p in self.participants:
                    if not getattr(p.character_data, 'is_player', False) and p.is_defeated():
                        if p.difficulty == 'H': total_xp += 25; total_skill_xp += 10
                        else: total_xp += 10; total_skill_xp += 5
                        total_cc += renpy.random.randint(1, 100)
                player_stats.base_xp += total_xp
                player_stats.skill_xp += total_skill_xp
                outcome, rewards_summary = "Victory", "Drops: {}xp, {} skill xp, {}cc".format(total_xp, total_skill_xp, total_cc)
            else:
                outcome, rewards_summary = "Defeat", "You were defeated."
            self._log_event({"event_type": "combat_end", "outcome": outcome, "rewards": rewards_summary, "participants": self.participants})

        def _finalize_initiative_and_start_combat(self):
            """Finalize initiative order and start combat after all rolls are complete"""
            self.turn_order = sorted(self.participants, key=lambda c: c.initiative, reverse=True)
            self.combat_state = 'active'
            self._log_event({"event_type": "combat_start", "turn_order": [c.get_name() for c in self.turn_order]})
            self._log_event({"event_type": "round_start", "round_number": self.round_number})
            self._process_npc_turn_if_applicable()

        def process_player_initiative_roll(self, total_initiative_roll):
            """Process the player's manual initiative roll"""
            if self.combat_state != 'awaiting_initiative_roll' or not self.pending_initiative_rolls:
                return
            
            player_combatant = next((c for c in self.pending_initiative_rolls if getattr(c.character_data, 'is_player', False)), None)
            
            if player_combatant:
                player_combatant.initiative = total_initiative_roll
                self.pending_initiative_rolls.remove(player_combatant)
                self.player_initiative_rolled = True
                
                dex_mod = get_ability_modifier(player_combatant.character_data.dexterity)
                d20_roll = total_initiative_roll - dex_mod
                self._log_event({
                    "event_type": "initiative_roll", 
                    "actor_name": player_combatant.get_name(),
                    "d20_roll": d20_roll,
                    "dex_modifier": dex_mod,
                    "total_initiative": total_initiative_roll
                })
                
                if not self.pending_initiative_rolls:
                    self._finalize_initiative_and_start_combat()

        def _log_event(self, event):
            self.mechanical_log.append(event)
            if self.narrative_generator and event.get("event_type") not in ["initiative_prompt", "initiative_roll", "prompt_damage"]:
                prose = self.narrative_generator.generate_event_prose(event)
                if prose:
                    self.narrative_log.append(prose)
            renpy.restart_interaction()
