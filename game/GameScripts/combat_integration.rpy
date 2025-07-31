#============================================================================
# COMBAT SYSTEM INTEGRATION FUNCTIONS
#============================================================================
# This file contains functions that integrate the new enhanced combat system
# with the existing GUI and game mechanics
#============================================================================

init python:
    def select_action(action_data):
        """Handle action selection from the combat GUI"""
        global selected_action
        selected_action = action_data
        
    def confirm_action(action_data, target):
        """Process a confirmed combat action using the enhanced system with player-driven rolls"""
        global selected_action, selected_target, pending_roll
        
        current_participant = enhanced_combat_controller.get_current_participant()
        
        if action_data.get("type") == "weapon_attack":
            weapon = action_data.get("weapon")
            weapon_name = weapon.name if weapon else "weapon"
            
            # Calculate attack bonus for the dice roll
            str_mod = (getattr(current_participant, 'strength', 10) - 10) // 2
            prof_bonus = getattr(current_participant, 'proficiency_bonus', 2)
            weapon_bonus = getattr(current_participant, 'atk_bonus', 0)
            total_attack_bonus = str_mod + prof_bonus + weapon_bonus
            
            # Store the pending action and target for processing after roll
            pending_roll = {
                "action": action_data,
                "target": target,
                "attacker": current_participant,
                "weapon_name": weapon_name,
                "attack_bonus": total_attack_bonus
            }
            
            # Queue the attack roll for player input
            queue_dice_roll(
                dice_type="d20", 
                modifier=total_attack_bonus, 
                context="attack", 
                advantage=dice_advantage_state == "advantage", 
                disadvantage=dice_advantage_state == "disadvantage", 
                label=f"Attack with {weapon_name}"
            )
            
        elif action_data.get("type") == "defend":
            # Handle defend action (no roll needed)
            enhanced_combat_controller.process_defend(current_participant)
            
        elif action_data.get("type") == "escape":
            # Calculate escape DC and queue roll
            dex_mod = (getattr(current_participant, 'dexterity', 10) - 10) // 2
            
            pending_roll = {
                "action": action_data,
                "target": None,
                "attacker": current_participant,
                "escape_dc": 15  # Standard escape DC
            }
            
            # Queue the escape roll
            queue_dice_roll(
                dice_type="d20", 
                modifier=dex_mod, 
                context="save", 
                advantage=dice_advantage_state == "advantage", 
                disadvantage=dice_advantage_state == "disadvantage", 
                label="Escape Attempt"
            )
            
        elif action_data.get("type") == "unarmed_attack":
            # Process unarmed attack
            attack_entry = enhanced_combat_controller.process_attack(
                attacker=current_participant,
                target=target,
                weapon_name="fists",
                advantage=dice_advantage_state == "advantage",
                disadvantage=dice_advantage_state == "disadvantage"
            )
            
            # Generate narrative
            narrative = combat_narrative_generator.generate_attack_narrative(
                attacker=current_participant,
                target=target,
                roll_data=attack_entry.roll_result,
                hit_result=attack_entry.status,
                damage_data=attack_entry.damage,
                weapon_name="fists"
            )
            
            enhanced_combat_controller.add_narrative(narrative)
            
        elif action_data.get("type") == "defend":
            # Process defensive action
            log_entry = CombatLogEntry(
                round_num=enhanced_combat_controller.round_number,
                participant=current_participant,
                action_type="defend",
                status="defended"
            )
            enhanced_combat_controller.combat_log.append(log_entry)
            
            # Generate defensive narrative
            narrative = combat_narrative_generator.generate_defense_narrative(current_participant)
            enhanced_combat_controller.add_narrative(narrative)
            
        elif action_data.get("type") == "escape":
            # Process escape attempt
            dex_mod = (getattr(current_participant, 'dexterity', 10) - 10) // 2
            escape_roll = DiceRoll(20, dex_mod, 
                                 dice_advantage_state == "advantage", 
                                 dice_advantage_state == "disadvantage")
            roll_result = escape_roll.roll()
            
            success = roll_result['total'] >= 15  # DC 15 escape
            
            log_entry = CombatLogEntry(
                round_num=enhanced_combat_controller.round_number,
                participant=current_participant,
                action_type="escape",
                roll_result=roll_result,
                status="success" if success else "failed"
            )
            enhanced_combat_controller.combat_log.append(log_entry)
            
            if success:
                narrative = f"{current_participant.name} successfully escapes from combat!"
            else:
                narrative = f"{current_participant.name} attempts to flee but cannot break away from the fight."
            
            enhanced_combat_controller.add_narrative(narrative)
        
        # Advance turn
        enhanced_combat_controller.advance_turn()
        
        # Clear selections
        selected_action = None
        selected_target = None
        
        # Reset advantage state
        store.dice_advantage_state = "normal"
        
    def process_npc_turn():
        """Process an NPC's turn using the enhanced combat system"""
        current_participant = enhanced_combat_controller.get_current_participant()
        
        if not current_participant or current_participant == player_stats:
            return
            
        # Ensure the target is definitely the player, not the current NPC
        target = player_stats
        
        # Debugging: Verify we have the right attacker and target
        if current_participant == target:
            # This should never happen! Fix the targeting
            return
            
        # Simple AI: NPC attacks the player
        # Calculate NPC attack bonus
        str_mod = (getattr(current_participant, 'strength', 10) - 10) // 2
        prof_bonus = getattr(current_participant, 'proficiency_bonus', 2)
        weapon_bonus = getattr(current_participant, 'atk_bonus', 0)
        total_attack_bonus = str_mod + prof_bonus + weapon_bonus
        
        # Process NPC attack using enhanced system
        attack_entry = enhanced_combat_controller.process_attack(
            attacker=current_participant,
            target=target,  # This should always be player_stats
            weapon_name="weapon"  # Generic weapon for NPCs
        )
        
        # Since you removed narrative display, skip narrative generation for now
        # Will rebuild this when we restore the narrative section
        
        # Advance turn to next participant
        enhanced_combat_controller.advance_turn()
        sync_combat_state()
        
    def process_dice_roll_result(roll_result):
        """Process a completed dice roll and apply it to the pending combat action"""
        global pending_roll
        
        if not pending_roll or not roll_result:
            return
            
        action_data = pending_roll.get("action")
        target = pending_roll.get("target")
        attacker = pending_roll.get("attacker")
        
        # Convert dice interface result to combat controller format
        combat_roll_result = {
            "d20": roll_result.chosen_roll if roll_result.chosen_roll else roll_result.raw_rolls[0],
            "modifier": roll_result.request.modifier,
            "total": roll_result.final_result,
            "advantage": roll_result.request.advantage,
            "disadvantage": roll_result.request.disadvantage,
            "rolls": roll_result.raw_rolls
        }
        
        if action_data.get("type") == "weapon_attack":
            # Process attack with player's roll result
            weapon_name = pending_roll.get("weapon_name", "weapon")
            
            # Determine if attack hits
            target_ac = getattr(target, 'ac', 10)
            natural_20 = combat_roll_result['d20'] == 20
            natural_1 = combat_roll_result['d20'] == 1
            
            if natural_1:
                # Critical miss
                hit = False
                critical = False
                status = "fumble"
            elif natural_20 or roll_result.final_result >= target_ac:
                # Hit (natural 20 is always a hit)
                hit = True
                # Critical hit on natural 20 OR exceeding AC by 7+
                critical = natural_20 or (roll_result.final_result - target_ac >= 7)
                status = "critical" if critical else "hit"
            else:
                # Miss
                hit = False
                critical = False
                status = "miss"
            
            # Create attack log entry with player's roll
            attack_entry = CombatLogEntry(
                round_num=enhanced_combat_controller.round_number,
                participant=attacker,
                action_type="attack",
                roll_result=combat_roll_result,
                target=target,
                status=status
            )
            
            if hit:
                # Attack hits - calculate damage
                weapon = action_data.get("weapon")
                damage_dice = getattr(weapon, 'damage_dice', "1d6") if weapon else "1d6"
                
                # Calculate damage bonus
                str_mod = (getattr(attacker, 'strength', 10) - 10) // 2
                weapon_dmg_bonus = getattr(attacker, 'dmg_bonus', 0)
                total_damage_bonus = str_mod + weapon_dmg_bonus
                
                # Use the enhanced combat system's damage processing
                damage_result = enhanced_combat_controller.process_damage(attacker, target, weapon_name, critical)
                attack_entry.damage = damage_result
                
                # Apply damage to target
                if hasattr(target, 'hp') and damage_result['total'] > 0:
                    target.hp = max(0, target.hp - damage_result['total'])
                    
            # Add to enhanced combat log
            enhanced_combat_controller.combat_log.append(attack_entry)
            
            # Generate narrative
            narrative = combat_narrative_generator.generate_attack_narrative(
                attacker=attacker,
                target=target,
                roll_data=combat_roll_result,
                hit_result=status,
                damage_data=attack_entry.damage if hit else None,
                weapon_name=weapon_name
            )
            enhanced_combat_controller.add_narrative(narrative)
            
        elif action_data.get("type") == "damage":
            # Process damage roll result
            target = pending_roll.get("target")
            attacker = pending_roll.get("attacker")
            weapon_name = pending_roll.get("weapon_name", "weapon")
            critical = pending_roll.get("critical", False)
            attack_roll = pending_roll.get("attack_roll", 0)
            
            damage_amount = roll_result.final_result
            if critical:
                damage_amount *= 2  # Double damage for critical hits
                
            # Apply damage to target
            if hasattr(target, 'hp'):
                target.hp = max(0, target.hp - damage_amount)
                
            # Add to combat log
            enhanced_combat_controller.add_log_entry(
                participant=attacker,
                action="Attack",
                target=target.name if hasattr(target, 'name') else "Target",
                roll_result=attack_roll,
                status="Hit" + (" (Critical!)" if critical else ""),
                damage=damage_amount
            )
            
            # Clear pending roll and advance turn
            pending_roll = None
            enhanced_combat_controller.advance_turn()
            sync_combat_state()
            
        elif action_data.get("type") == "escape":
            # Process escape attempt with player's roll
            escape_dc = pending_roll.get("escape_dc", 15)
            
            # Create escape log entry
            escape_entry = CombatLogEntry(
                round_num=enhanced_combat_controller.round_number,
                participant=attacker,
                action_type="escape",
                roll_result=combat_roll_result,
                target=None,
                status="success" if roll_result.final_result >= escape_dc else "failed"
            )
            
            enhanced_combat_controller.combat_log.append(escape_entry)
            
            if roll_result.final_result >= escape_dc:
                # Escape successful
                narrative = f"{attacker.name} successfully escapes from combat!"
                enhanced_combat_controller.add_narrative(narrative)
                renpy.jump("combat_escape_success")
            else:
                # Escape failed
                narrative = f"{attacker.name} fails to escape and remains in combat!"
                enhanced_combat_controller.add_narrative(narrative)
                
            # Clear pending roll and advance turn
            pending_roll = None
            enhanced_combat_controller.advance_turn()
            sync_combat_state()
        
        # Clear pending roll and advance turn
        pending_roll = None
        enhanced_combat_controller.advance_turn()
        sync_combat_state()
        
    def initialize_enhanced_combat(participants):
        """Initialize a new combat encounter with the enhanced system"""
        global combat_participants, current_turn_index, combat_round
        
        # Initialize enhanced combat controller
        enhanced_combat_controller.initialize_combat(participants)
        
        # Update legacy variables for compatibility
        combat_participants = enhanced_combat_controller.participants[:]
        current_turn_index = enhanced_combat_controller.turn_index
        combat_round = enhanced_combat_controller.round_number
        
        # Add round start narrative
        narrative = combat_narrative_generator.generate_round_transition_narrative(combat_round)
        enhanced_combat_controller.add_narrative(narrative)
        
    def sync_combat_state():
        """Synchronize the enhanced combat state with legacy variables"""
        global current_turn_index, combat_round
        
        current_turn_index = enhanced_combat_controller.turn_index
        combat_round = enhanced_combat_controller.round_number
        
    def get_combat_status():
        """Get the current combat status for display"""
        if not enhanced_combat_controller.participants:
            return "No combat active"
            
        current = enhanced_combat_controller.get_current_participant()
        if current:
            return f"Round {enhanced_combat_controller.round_number} - {current.name}'s Turn"
        else:
            return f"Round {enhanced_combat_controller.round_number}"
            
    def end_combat(result_type="victory", victor=None):
        """End the current combat encounter"""
        narrative = combat_narrative_generator.generate_combat_end_narrative(victor, result_type)
        enhanced_combat_controller.add_narrative(narrative)
        
        # Clear combat state
        global combat_participants, current_turn_index, combat_round, selected_action, selected_target
        combat_participants = []
        current_turn_index = 0
        combat_round = 1
        selected_action = None
        selected_target = None
        
    def is_combat_over():
        """Check if combat should end"""
        if not enhanced_combat_controller.participants:
            return True
            
        # Check if player is defeated
        if player_stats.hp <= 0:
            return True
            
        # Check if all enemies are defeated
        enemies_alive = False
        for participant in enhanced_combat_controller.participants:
            if participant != player_stats and participant.hp > 0:
                enemies_alive = True
                break
                
        return not enemies_alive
        
    def get_combat_victor():
        """Determine the victor of combat"""
        if player_stats.hp <= 0:
            return None  # Player defeated
        else:
            return player_stats  # Player victorious

# Helper function for backwards compatibility with existing combat system
init python:
    def parse_combat_log_for_attacks():
        """Legacy function maintained for compatibility"""
        # This function is no longer needed with the enhanced system
        # but kept to avoid breaking existing code
        pass
