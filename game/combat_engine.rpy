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
        
        def add_status_effect(self, effect_name, duration=1):
            """Add a status effect with duration (turns remaining)"""
            self.status_effects.append({"name": effect_name, "duration": duration})
        
        def remove_status_effect(self, effect_name):
            """Remove a specific status effect"""
            self.status_effects = [effect for effect in self.status_effects if effect["name"] != effect_name]
        
        def has_status_effect(self, effect_name):
            """Check if combatant has a specific status effect"""
            return any(effect["name"] == effect_name for effect in self.status_effects)
        
        def update_status_effects(self):
            """Reduce duration of all status effects and remove expired ones"""
            for effect in self.status_effects[:]:
                effect["duration"] -= 1
                if effect["duration"] <= 0:
                    self.status_effects.remove(effect)
        
        def get_attack_roll_type(self):
            """Determine if this combatant has advantage, disadvantage, or normal roll"""
            if self.has_status_effect("disadvantage_next_attack"):
                return "disadvantage"
            elif self.has_status_effect("advantage_next_attack"):
                return "advantage"
            return "normal"

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
            # Allow turn advancement from defend menu states
            if self.combat_state not in ['active', 'awaiting_defend_choice']: return
            if self._check_combat_end(): return
            self.current_turn_index = (self.current_turn_index + 1) % len(self.turn_order)
            if self.current_turn_index == 0:
                self.round_number += 1
                self._log_event({"event_type": "round_start", "round_number": self.round_number})
            if self.turn_order:
                current_combatant = self.get_current_combatant()
                current_combatant.reset_turn_actions()
                # Update status effects at the start of each turn
                current_combatant.update_status_effects()
                # Remove single-use status effects after they're consumed
                if current_combatant.has_status_effect("disadvantage_next_attack") or current_combatant.has_status_effect("advantage_next_attack"):
                    current_combatant.remove_status_effect("disadvantage_next_attack")
                    current_combatant.remove_status_effect("advantage_next_attack")
                if current_combatant.is_defeated():
                    self.advance_turn()
                else:
                    self._process_npc_turn_if_applicable()

        def _process_npc_turn_if_applicable(self):
            # DISABLED: Automatic opponent actions now controlled by proceed button
            # This method is now only called for non-combat scenarios
            current_combatant = self.get_current_combatant()
            if not current_combatant or getattr(current_combatant.character_data, 'is_player', False):
                return
            # No automatic processing - wait for manual proceed button
            return

        def _process_npc_turn_manual(self):
            """Manually process NPC turn when proceed button is pressed"""
            current_combatant = self.get_current_combatant()
            if not current_combatant or getattr(current_combatant.character_data, 'is_player', False):
                return

            player_target = next((p for p in self.participants if getattr(p.character_data, 'is_player', False) and not p.is_defeated()), None)
            if player_target:
                npc_weapon = next((item for item in current_combatant.character_data.equipped_items if item.slot == 'weapon'), None)
                if npc_weapon:
                    # Handle advantage/disadvantage for NPC attacks
                    roll_type = current_combatant.get_attack_roll_type()
                    if roll_type == "advantage":
                        roll1 = renpy.random.randint(1, 20)
                        roll2 = renpy.random.randint(1, 20)
                        d20_roll = max(roll1, roll2)
                        roll_display = "Advantage: {} and {} (using {})".format(roll1, roll2, d20_roll)
                    elif roll_type == "disadvantage":
                        roll1 = renpy.random.randint(1, 20)
                        roll2 = renpy.random.randint(1, 20)
                        d20_roll = min(roll1, roll2)
                        roll_display = "Disadvantage: {} and {} (using {})".format(roll1, roll2, d20_roll)
                    else:
                        d20_roll = renpy.random.randint(1, 20)
                        roll_display = str(d20_roll)
                    
                    # Store attack data for later resolution
                    self.pending_attack = {
                        "actor": current_combatant,
                        "target": player_target,
                        "weapon": npc_weapon,
                        "d20_roll": d20_roll,
                        "roll_type": roll_type,
                        "roll_display": roll_display
                    }
                    # Announce the attack but don't resolve it yet
                    self._announce_npc_attack(current_combatant, player_target, npc_weapon, d20_roll, roll_display)
            
            if self.combat_state == 'active':
                self.combat_state = 'awaiting_attack_resolution'
                self._log_event({
                    "event_type": "attack_announced_pause",
                    "message": "Attack announced. Click PROCEED to see the results."
                })

        def _announce_npc_attack(self, actor, target, weapon, d20_roll, roll_display=None):
            """Announce the opponent's attack without resolving it yet"""
            str_mod = get_ability_modifier(actor.character_data.strength)
            atk_bonus = actor.character_data.atk_bonus
            prof_bonus = actor.character_data.proficiency_bonus
            total_attack_roll = d20_roll + str_mod + prof_bonus + atk_bonus
            target_ac = target.get_ac()
            
            # Log the attack announcement (what they're attempting)
            attack_announcement = {
                "event_type": "attack_announcement",
                "actor": actor,
                "target": target,
                "weapon": weapon,
                "actor_name": actor.get_name(),
                "target_name": target.get_name(),
                "weapon_name": weapon.name,
                "d20_roll": d20_roll,
                "total_attack_roll": total_attack_roll,
                "target_ac": target_ac
            }
            self._log_event(attack_announcement)
            actor.action_taken = True

        def _resolve_pending_attack(self):
            """Resolve the pending attack that was announced"""
            if not hasattr(self, 'pending_attack') or not self.pending_attack:
                return
                
            attack_data = self.pending_attack
            actor = attack_data["actor"]
            target = attack_data["target"]
            weapon = attack_data["weapon"]
            d20_roll = attack_data["d20_roll"]
            
            # Resolve only the outcome part (no duplicate attack initiation)
            self._resolve_npc_attack_outcome(actor, target, weapon, d20_roll)
            
            # Clear the pending attack
            self.pending_attack = None
            
            # Set state to await final proceed
            if self.combat_state == 'awaiting_attack_resolution':
                self.combat_state = 'awaiting_post_action_proceed'
                self._log_event({
                    "event_type": "post_action_pause",
                    "message": "Opponent action complete. Click PROCEED to continue."
                })

        def _resolve_npc_attack_outcome(self, actor, target, weapon, d20_roll):
            """Resolve only the outcome of an already-announced NPC attack (no duplicate initiation narrative)"""
            str_mod = get_ability_modifier(actor.character_data.strength)
            atk_bonus = actor.character_data.atk_bonus
            prof_bonus = actor.character_data.proficiency_bonus
            total_attack_roll = d20_roll + str_mod + prof_bonus + atk_bonus
            target_ac = target.get_ac()
            is_critical_hit = (d20_roll == 20) or (total_attack_roll - target_ac >= 7)
            is_critical_fumble = (d20_roll == 1)
            hit = not is_critical_fumble and (is_critical_hit or total_attack_roll >= target_ac)

            # Log attack resolution event (outcome only, no initiation narrative)
            attack_resolution_event = {
                "event_type": "attack_resolution_outcome", 
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
            self._log_event(attack_resolution_event)

            if hit:
                damage_dice = weapon.effects.get("damage", "1d4")
                if is_critical_hit:
                    try:
                        num_dice = int(damage_dice.split('d')[0]) * 2
                        damage_dice = "{}d{}".format(num_dice, damage_dice.split('d')[1])
                    except: pass
                damage_roll = roll_dice(damage_dice)
                total_damage = max(1, damage_roll + str_mod + actor.character_data.dmg_bonus)
                
                # Apply block damage reduction if target has block status effect
                final_damage = total_damage
                if target.has_status_effect("block_next_attack"):
                    block_percentage = getattr(target, 'block_percentage', 0)
                    damage_reduction = int(total_damage * block_percentage / 100)
                    final_damage = max(1, total_damage - damage_reduction)  # Minimum 1 damage
                    
                    # Log the block effect with clear before/after damage
                    self._log_event({
                        "event_type": "block_effect",
                        "target_name": target.get_name(),
                        "original_damage": total_damage,
                        "final_damage": final_damage,
                        "block_percentage": block_percentage,
                        "message": "{} damage reduced to {} damage by block ({}% reduction)".format(total_damage, final_damage, block_percentage)
                    })
                    
                    # Remove the block status effect after use
                    target.remove_status_effect("block_next_attack")
                    if hasattr(target, 'block_percentage'):
                        delattr(target, 'block_percentage')
                
                target.take_damage(final_damage)

                damage_event = {
                    "event_type": "damage_resolution", 
                    "actor": actor,
                    "target": target,
                    "actor_name": actor.get_name(), 
                    "target_name": target.get_name(), 
                    "total_damage": final_damage, 
                    "target_hp_remaining": target.current_hp, 
                    "target_is_defeated": target.is_defeated()
                }
                self._log_event(damage_event)

                if target.is_defeated() and not target.is_finished:
                    self.resolve_finishing_blow("nonlethal", npc_actor=actor)

        def _proceed_after_opponent_action(self):
            """Continue combat flow after opponent action pause"""
            if self.combat_state == 'awaiting_post_action_proceed':
                self.combat_state = 'active'
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
            
            # Apply block damage reduction if target has block status effect
            if target.has_status_effect("block_next_attack"):
                block_percentage = getattr(target, 'block_percentage', 0)
                damage_reduction = int(final_damage_to_apply * block_percentage / 100)
                final_damage_to_apply = max(1, final_damage_to_apply - damage_reduction)  # Minimum 1 damage
                
                # Log the block effect with clear before/after damage
                self._log_event({
                    "event_type": "block_effect",
                    "target_name": target.get_name(),
                    "original_damage": max(1, total_damage),
                    "damage_reduction": damage_reduction,
                    "final_damage": final_damage_to_apply,
                    "block_percentage": block_percentage,
                    "message": "{} damage reduced to {} damage by block ({}% reduction)".format(max(1, total_damage), final_damage_to_apply, block_percentage)
                })
                
                # Remove the block status effect after use
                target.remove_status_effect("block_next_attack")
                if hasattr(target, 'block_percentage'):
                    delattr(target, 'block_percentage')
            
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
                
                # Apply block damage reduction if target has block status effect
                final_damage = total_damage
                if target.has_status_effect("block_next_attack"):
                    block_percentage = getattr(target, 'block_percentage', 0)
                    damage_reduction = int(total_damage * block_percentage / 100)
                    final_damage = max(1, total_damage - damage_reduction)  # Minimum 1 damage
                    
                    # Log the block effect with clear before/after damage
                    self._log_event({
                        "event_type": "block_effect",
                        "target_name": target.get_name(),
                        "original_damage": total_damage,
                        "damage_reduction": damage_reduction,
                        "final_damage": final_damage,
                        "block_percentage": block_percentage,
                        "message": "{} damage reduced to {} damage by block ({}% reduction)".format(total_damage, final_damage, block_percentage)
                    })
                    
                    # Remove the block status effect after use
                    target.remove_status_effect("block_next_attack")
                    if hasattr(target, 'block_percentage'):
                        delattr(target, 'block_percentage')
                
                target.take_damage(final_damage)

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
