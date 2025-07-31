#============================================================================
# COMBAT ENCOUNTER GUI SYSTEM
#============================================================================
# This screen provides the main combat interface, displaying:
# - All participant stats and status
# - Initiative/turn order
# - Available combat actions with mechanic previews
# - Roll interface for d20 system
# - Combat narration and environmental context
#============================================================================

# Combat state variables
default combat_participants = []
default current_turn_index = 0
default combat_round = 1
default combat_log = []
default pending_roll = None
default pending_damage_roll = None
default selected_action = None
default selected_target = None

# Main combat encounter screen
screen combat_encounter():
    modal True
    
    frame:
        style "combat_main_frame"
        xsize 3850
        ysize 1720
        xalign 0.5
        yalign 0.5
        
        hbox:
            spacing 20
            xfill True
            
            # LEFT PANEL: PARTICIPANT STATS
            frame:
                style "combat_stats_frame"
                xsize 600
                ysize 1675
                
                vbox:
                    spacing 10
                    
                    # Combat info header
                    frame:
                        xsize 580
                        background "#333333"
                        padding (10, 10)
                        
                        vbox:
                            spacing 5
                            text "ROUND [combat_round]" color "#FFD700" size 24 bold True
                            
                            if combat_participants:
                                $ current_participant = combat_participants[current_turn_index]
                                text "[current_participant.name]'S TURN" style "combat_mechanical_text"
                            
                            text "INITIATIVE ORDER:" style "combat_mechanical_text_sub1"
                            
                            for i, participant in enumerate(combat_participants):
                                $ is_current = (i == current_turn_index)
                                $ status_color = "#FFD700" if is_current else "#FFFFFF"
                                
                                hbox:
                                    spacing 10
                                    if is_current:
                                        text "►" color "#FFD700" size 20
                                    else:
                                        text " " size 20
                                    text "[participant.name]" color status_color size 18
                    
                    # Participant stats viewport
                    viewport:
                        xsize 580
                        ysize 1375
                        scrollbars "vertical"
                        mousewheel True
                        
                        vbox:
                            spacing 15
                            
                            for participant in combat_participants:
                                frame:
                                    background "#333333"
                                    padding (10, 10)
                                    xsize 560
                                    
                                    vbox:
                                        spacing 8
                                        
                                        # Name and status
                                        hbox:
                                            spacing 10
                                            text "[participant.name]" color "#FFFFFF" size 20 bold True
                                            if participant == player_stats:
                                                text "(YOU)" color "#00FF00" size 14
                                        
                                        # Health bar
                                        $ hp_percent = float(participant.hp) / float(participant.max_hp)
                                        $ hp_color = "#00FF00" if hp_percent > 0.6 else "#FFFF00" if hp_percent > 0.3 else "#FF0000"
                                        
                                        hbox:
                                            spacing 5
                                            text "HP:" style "combat_stats_text"
                                            bar:
                                                value participant.hp
                                                range participant.max_hp
                                                xsize 200
                                                ysize 20
                                                left_bar hp_color
                                                right_bar "#333333"
                                            text "[participant.hp]/[participant.max_hp]" color "#FFFFFF" size 24
                                        
                                        # Combat stats
                                        grid 2 4:
                                            spacing 5
                                            text "AC:" style "combat_stats_text"
                                            text "[participant.ac]" style "combat_mechanical_text_sub1"
                                            text "ATK:" style "combat_stats_text"
                                            text "+[participant.atk_bonus]" style "combat_mechanical_text_sub1"
                                            text "DMG:" style "combat_stats_text"
                                            text "+[participant.dmg_bonus]" style "combat_mechanical_text_sub1"
                                            text "PROF:" style "combat_stats_text"
                                            text "+[participant.proficiency_bonus]" style "combat_mechanical_text_sub1"
                                        
                                        # Equipment
                                        if hasattr(participant, 'status_effects') and participant.status_effects:
                                            text "STATUS:" color "#FF6600" size 24 bold True
                                            for effect in participant.status_effects:
                                                text "• [effect]" color "#FFAA66" size 24
            
            # CENTER PANEL: SPLIT BETWEEN NARRATIVE AND MECHANICAL LOG
            vbox:
                spacing 20
                xsize 2560
                
                 
                # BOTTOM HALF: MECHANICAL COMBAT LOG
                frame:
                    style "combat_log_frame"
                    xsize 2560
                    ysize 600
                    
                    vbox:
                        spacing 10
                        
                        text "COMBAT LOG (MECHANICAL)" style "combat_mechanical_text" xalign 0.5
                        
                        viewport:
                            xsize 2540
                            ysize 550
                            scrollbars "vertical"
                            mousewheel True
                            
                            vbox:
                                spacing 10
                                
                                # Display mechanical log from enhanced combat controller
                                if hasattr(enhanced_combat_controller, 'combat_log') and enhanced_combat_controller.combat_log:
                                    for log_entry in enhanced_combat_controller.combat_log:
                                        frame:
                                            background "#333333"
                                            padding (10, 10)
                                            xsize 2480
                                            
                                            vbox:
                                                spacing 5
                                                
                                                # Display formatted mechanical information
                                                $ formatted_display = log_entry.format_mechanical_display()
                                                for line in formatted_display.split("\n"):
                                                    if line.strip():
                                                        # Color code different types of information
                                                        if "Round" in line and "|" in line:
                                                            text "[line]" color "#FFD700" size 20 bold True
                                                        elif "Roll:" in line:
                                                            text "[line]" color "#00CCFF" size 18
                                                        elif "Damage:" in line:
                                                            text "[line]" color "#FF6666" size 18
                                                        elif "HIT" in line or "CRITICAL" in line:
                                                            text "[line]" color "#00FF00" size 18
                                                        elif "MISS" in line or "FUMBLE" in line:
                                                            text "[line]" color "#FF9999" size 18
                                                        else:
                                                            text "[line]" color "#FFFFFF" size 18
                                else:
                                    # Placeholder for when no combat has started
                                    frame:
                                        background "#333333"
                                        padding (15, 15)
                                        xsize 2480
                                        
                                        text "Combat has not yet begun. Mechanical details will appear here during fights." color "#888888" size 20 italic True xalign 0.5 text_align 0.5
                    
                   
            
            # RIGHT PANEL: ENHANCED DICE INTERFACE
            frame:
                style "combat_log_frame"
                xsize 600
                ysize 1675
                xalign 1.0
                
                # Use the new enhanced dice interface
                use enhanced_dice_interface
        
        # BOTTOM PANEL: ACTION BUTTONS  
        frame:
            style "combat_action_frame"
            xsize 5120
            ysize 300
            xalign 0.5
            ypos 1575
            
            hbox:
                spacing 50
                xalign 0.5
                yalign 0.5
                
                # Combat Action Buttons
                hbox:
                    spacing 40
                    xalign 0.5
                    yalign 0.5
                    
                    textbutton "ATTACK":
                        background "#AA0000"
                        hover_background "#CC3333"
                        text_color "#FFFFFF"
                        text_hover_color "#FFFF00"
                        text_size 24
                        xsize 200
                        ysize 60
                        action Function(select_combat_action, "attack")
                    
                    textbutton "DEFEND":
                        background "#0066AA"
                        hover_background "#3388CC"
                        text_color "#FFFFFF"
                        text_hover_color "#FFFF00"
                        text_size 24
                        xsize 200
                        ysize 60
                        action Function(select_combat_action, "defend")
                    
                    textbutton "UTILITY":
                        background "#6600AA"
                        hover_background "#8833CC"
                        text_color "#FFFFFF"
                        text_hover_color "#FFFF00"
                        text_size 24
                        xsize 200
                        ysize 60
                        action Function(select_combat_action, "utility")
                    
                    textbutton "ITEM":
                        background "#AA6600"
                        hover_background "#CC8833"
                        text_color "#FFFFFF"
                        text_hover_color "#FFFF00"
                        text_size 24
                        xsize 200
                        ysize 60
                        action Function(select_combat_action, "item")
        # Vertical control buttons with hover effects
        hbox:
            xpos 7
            ypos 1600
            spacing 30
            
            textbutton "END TURN":
                background "#666666"
                hover_background "#888888"
                text_color "#FFFFFF"
                text_hover_color "#FFFF00"
                text_size 22
                xsize 175
                ysize 50
                action Function(handle_end_turn)
            
            textbutton "FLEE COMBAT":
                background "#AA0000"
                hover_background "#CC3333"
                text_color "#FFFFFF"
                text_hover_color "#FFFF00"
                text_size 22
                xsize 180
                ysize 50
                action Function(attempt_combat_escape)
            
            textbutton "EXIT COMBAT":
                background "#333333"
                hover_background "#555555"
                text_color "#FFFFFF"
                text_hover_color "#FFFF00"
                text_size 22
                xsize 175
                ysize 50
                action Return()

# Combat system functions
init python:
    def select_combat_action(action_type):
        """Handle combat action selection with enhanced combat system"""
        global selected_action, selected_target, enhanced_combat_controller
        
        # Initialize enhanced combat controller with current participants if needed
        if not hasattr(store, 'enhanced_combat_controller') or store.enhanced_combat_controller is None:
            store.enhanced_combat_controller = CombatController()
            enhanced_combat_controller = store.enhanced_combat_controller
        else:
            enhanced_combat_controller = store.enhanced_combat_controller
        
        # Ensure controller is initialized with current participants
        if not enhanced_combat_controller.participants and combat_participants:
            enhanced_combat_controller.initialize_combat(combat_participants)
        
        # Determine weapon for attack actions
        weapon = None
        if action_type == "attack" and hasattr(player_stats, 'equipped_items') and player_stats.equipped_items:
            for item in player_stats.equipped_items:
                if hasattr(item, 'category') and item.category == "equippable" and getattr(item, 'slot', '') == "weapon":
                    weapon = item
                    break
        
        if action_type == "attack":
            # Set up weapon attack action
            action_data = {"type": "weapon_attack", "weapon": weapon}
            # Auto-target first available enemy
            target = get_first_enemy_target()
            if target:
                selected_action = action_data
                selected_target = target
                # Use the enhanced system's confirm_action function
                confirm_action(action_data, target)
        elif action_type == "defend":
            # Set up defend action
            action_data = {"type": "defend"}
            selected_action = action_data
            # Use the enhanced system's confirm_action function  
            confirm_action(action_data, None)
        elif action_type == "utility":
            # Set up escape action
            action_data = {"type": "escape"}
            selected_action = action_data
            # Use the enhanced system's confirm_action function
            confirm_action(action_data, None)
        elif action_type == "item":
            # Set up item action (placeholder for now)
            action_data = {"type": "item"}
            selected_action = action_data
            # Just use select_action for now since item usage isn't fully implemented
            select_action(action_data)
    
    def get_first_enemy_target():
        """Get the first available enemy target"""
        for participant in combat_participants:
            if participant != player_stats and getattr(participant, 'hp', 0) > 0:
                return participant
        return None
    
    def initialize_enhanced_combat_if_needed():
        """Initialize enhanced combat controller if needed"""
        global enhanced_combat_controller
        if enhanced_combat_controller is None:
            # Import the controller class
            enhanced_combat_controller = CombatController()
            if combat_participants:
                enhanced_combat_controller.initialize_combat(combat_participants)
    
    def handle_end_turn():
        """Handle end turn button logic"""
        if not combat_participants or current_turn_index >= len(combat_participants):
            return
        
        # Initialize enhanced combat controller if needed
        initialize_enhanced_combat_if_needed()
        
        current_participant = combat_participants[current_turn_index]
        if current_participant == player_stats:
            # Use enhanced system for turn handling
            if hasattr(enhanced_combat_controller, 'advance_turn'):
                enhanced_combat_controller.advance_turn()
                sync_combat_state()
            else:
                end_player_turn()
    
    def process_npc_turn():
        """Process NPC turn with simple AI"""
        if not combat_participants or current_turn_index >= len(combat_participants):
            return
        
        current_npc = combat_participants[current_turn_index]
        if current_npc == player_stats:
            return
        
        # Simple AI: attack player
        target = player_stats
        weapon = current_npc.equipped_items[0] if current_npc.equipped_items else None
        
        import random
        attack_roll = random.randint(1, 20)
        str_mod = (current_npc.strength - 10) // 2
        attack_total = attack_roll + current_npc.atk_bonus + str_mod
        
        weapon_name = weapon.name if weapon else "bare hands"
        
        if attack_roll == 1:
            log_message = f"{current_npc.name} critically fails with {weapon_name}!"
        elif attack_total >= target.ac:
            if weapon:
                damage_dice = weapon.effects.get("damage", "1d4")
                damage = roll_damage_dice(damage_dice) + str_mod
            else:
                damage = 1 + str_mod
            
            damage = max(1, damage)
            target.hp = max(0, target.hp - damage)
            
            if attack_roll == 20:
                log_message = f"CRITICAL! {current_npc.name} hits {target.name} for {damage} damage!"
            else:
                log_message = f"{current_npc.name} hits {target.name} for {damage} damage!"
        else:
            log_message = f"{current_npc.name} misses {target.name}!"
        
        combat_log.append(log_message)
        end_turn()
    
    def roll_damage_dice(dice_string):
        """Roll damage dice"""
        import random
        if 'd' not in dice_string:
            return int(dice_string)
        
        num_dice, die_size = dice_string.split('d')
        total = 0
        for _ in range(int(num_dice)):
            total += random.randint(1, int(die_size))
        return total
    
    def execute_roll(roll_data):
        """Execute pending roll"""
        import random
        
        action_data = roll_data["action"]
        target = roll_data["target"]
        d20_result = random.randint(1, 20)
        
        if action_data["type"] in ["weapon_attack", "unarmed_attack"]:
            str_mod = (player_stats.strength - 10) // 2
            dex_mod = (player_stats.dexterity - 10) // 2
            attack_total = d20_result + player_stats.atk_bonus + str_mod
            
            # Create enhanced combat narrative entry
            enhanced_entry = {
                "action_data": action_data,
                "actor": player_stats,
                "target": target,
                "result": {
                    "d20_roll": d20_result,
                    "attack_roll": attack_total,
                    "hit": attack_total >= target.ac and d20_result != 1
                }
            }
            
            # Initialize combat_narrative if it doesn't exist
            if not hasattr(store, 'combat_narrative'):
                store.combat_narrative = []
            
            if d20_result == 1:
                enhanced_entry["result"]["hit"] = False
                enhanced_entry["narrative"] = "Critical failure! Something goes terribly wrong..."
                store.combat_narrative.append(enhanced_entry)
                combat_log.append("CRITICAL FAILURE!")
            elif attack_total >= target.ac:
                # HIT - Prompt player for damage roll
                if action_data["type"] == "weapon_attack":
                    weapon = action_data["weapon"]
                    damage_dice = weapon.effects.get("damage", "1d4")
                    enhanced_entry["narrative"] = f"Roll {damage_dice} + {str_mod} STR for damage!"
                else:
                    damage_dice = "1"
                    enhanced_entry["narrative"] = f"Roll 1 + {str_mod} STR for unarmed damage!"
                
                # Set pending damage roll
                global pending_damage_roll
                pending_damage_roll = {
                    "action_data": action_data,
                    "target": target,
                    "damage_dice": damage_dice,
                    "str_mod": str_mod,
                    "critical": d20_result == 20 or attack_total >= target.ac + 7
                }
                
                enhanced_entry["result"]["pending_damage"] = True
                store.combat_narrative.append(enhanced_entry)
                
                if d20_result == 20 or attack_total >= target.ac + 7:
                    combat_log.append(f"CRITICAL HIT vs {target.name}! Roll for damage (double dice)!")
                else:
                    combat_log.append(f"Hit vs {target.name}! Roll for damage!")
            else:
                enhanced_entry["result"]["hit"] = False
                store.combat_narrative.append(enhanced_entry)
                combat_log.append(f"Miss! Attack vs {target.name} fails.")
        
        store.pending_roll = None
        end_player_turn()
    
    def execute_damage_roll(damage_result):
        """Execute damage roll with player input"""
        global pending_damage_roll
        
        if not pending_damage_roll:
            return
            
        damage_data = pending_damage_roll
        target = damage_data["target"]
        str_mod = damage_data["str_mod"]
        is_critical = damage_data["critical"]
        
        # Calculate total damage
        total_damage = max(1, damage_result + str_mod)
        
        # Apply damage
        target.hp = max(0, target.hp - total_damage)
        
        # Create enhanced combat narrative entry
        enhanced_entry = {
            "action_data": damage_data["action_data"],
            "actor": player_stats,
            "target": target,
            "result": {
                "damage_roll": damage_result,
                "str_modifier": str_mod,
                "total_damage": total_damage,
                "critical": is_critical,
                "target_remaining_hp": target.hp
            }
        }
        
        # Initialize combat_narrative if it doesn't exist
        if not hasattr(store, 'combat_narrative'):
            store.combat_narrative = []
        if not hasattr(store, 'combat_narrative_adjustment'):
            store.combat_narrative_adjustment = ui.adjustment(ranged=ui.adjustment())
        
        if is_critical:
            enhanced_entry["narrative"] = f"CRITICAL! {damage_result} + {str_mod} STR = {total_damage} damage!"
            store.combat_narrative.append(enhanced_entry)
            combat_log.append(f"CRITICAL DAMAGE! {total_damage} damage to {target.name}!")
        else:
            enhanced_entry["narrative"] = f"{damage_result} + {str_mod} STR = {total_damage} damage!"
            store.combat_narrative.append(enhanced_entry)
            combat_log.append(f"{total_damage} damage to {target.name}!")
        
        if target.hp <= 0:
            combat_log.append(f"{target.name} is defeated!")
        
        # Clear pending damage roll
        pending_damage_roll = None
        end_player_turn()
    
    def end_player_turn():
        """End player turn"""
        combat_log.append(f"{player_stats.name} ends turn.")
        end_turn()
    
    def end_turn():
        """Advance to next turn"""
        global current_turn_index, combat_round
        current_turn_index += 1
        if current_turn_index >= len(combat_participants):
            current_turn_index = 0
            combat_round += 1
            combat_log.append(f"=== ROUND {combat_round} ===")
    
    def select_action(action_data):
        """Select an action for the player to take"""
        global selected_action
        selected_action = action_data
        combat_log.append(f"{player_stats.name} prepares {action_data['type'].replace('_', ' ')}...")
    
    # Note: confirm_action function is provided by GameScripts/combat_integration.rpy
    
    def attempt_combat_escape():
        """Attempt to flee combat"""
        import random
        dex_mod = (player_stats.dexterity - 10) // 2
        escape_roll = random.randint(1, 20) + dex_mod
        
        if escape_roll >= 15:
            combat_log.append("Successfully fled combat!")
            renpy.return_statement()
        else:
            combat_log.append("Failed to flee!")
    
    def create_opponent_attack_entry(attacker, target, attack_roll, damage_roll, hit, weapon=None):
        """Create enhanced combat narrative entry for opponent attacks"""
        import random
        
        # Get attacker stats
        str_mod = getattr(attacker, 'str_mod', 0)
        dex_mod = getattr(attacker, 'dex_mod', 0)
        prof_bonus = getattr(attacker, 'proficiency_bonus', 2)  # Default for NPCs
        
        # Determine attack type and create action data
        if weapon:
            action_data = {
                "type": "weapon_attack",
                "weapon": weapon
            }
            # Calculate d20 result from total
            is_finesse = weapon.effects.get('finesse', False) if hasattr(weapon, 'effects') else False
            is_ranged = weapon.effects.get('ranged', False) if hasattr(weapon, 'effects') else False
            ability_mod = dex_mod if (is_ranged or is_finesse) else str_mod
            d20_result = attack_roll - ability_mod - prof_bonus
        else:
            action_data = {
                "type": "unarmed_attack"
            }
            ability_mod = str_mod
            d20_result = attack_roll - str_mod - prof_bonus
        
        # Ensure d20 result is valid
        d20_result = max(1, min(20, d20_result))
        
        # Create enhanced entry
        enhanced_entry = {
            "action_data": action_data,
            "actor": attacker,
            "target": target,
            "result": {
                "attack_roll": attack_roll,
                "d20_roll": d20_result,
                "damage_roll": damage_roll,
                "hit": hit,
                "ability_modifier": ability_mod,
                "proficiency_bonus": prof_bonus
            }
        }
        
        # Initialize combat_narrative if it doesn't exist
        if not hasattr(store, 'combat_narrative'):
            store.combat_narrative = []
        
        # Add to combat narrative
        store.combat_narrative.append(enhanced_entry)
        
        # Auto-scroll to bottom
        if hasattr(store, 'combat_narrative_adjustment'):
            renpy.restart_interaction()
    
    def parse_combat_log_for_attacks():
        """Parse combat_log for opponent attack patterns and create enhanced entries"""
        if not hasattr(store, 'combat_log') or not store.combat_log:
            return
        
        # Initialize tracking
        if not hasattr(store, 'parsed_combat_entries'):
            store.parsed_combat_entries = set()
        if not hasattr(store, 'combat_narrative'):
            store.combat_narrative = []
        
        import re
        
        # Parse recent combat log entries for opponent attacks
        for i, entry in enumerate(store.combat_log):
            # Skip if already parsed
            entry_id = f"{i}_{entry}"
            if entry_id in store.parsed_combat_entries:
                continue
            
            # Look for opponent attack patterns
            # Pattern: "[NPC Name] attacks [Target] for [damage] damage!"
            attack_pattern = r"^(.+?)\s+attacks\s+(.+?)\s+for\s+(\d+)\s+damage!"
            hit_match = re.match(attack_pattern, entry)
            
            if hit_match:
                attacker_name = hit_match.group(1).strip()
                target_name = hit_match.group(2).strip()
                damage = int(hit_match.group(3))
                
                # Find attacker and target objects
                attacker = None
                target = None
                
                # Check combat participants
                if hasattr(store, 'combat_participants'):
                    for participant in store.combat_participants:
                        if hasattr(participant, 'name'):
                            if participant.name == attacker_name:
                                attacker = participant
                            elif participant.name == target_name:
                                target = participant
                
                # If we found both attacker and target, create enhanced entry
                if attacker and target:
                    # Estimate attack roll (AC + random factor)
                    import random
                    target_ac = getattr(target, 'ac', 10)
                    attack_roll = target_ac + random.randint(1, 8)  # Hit by 1-8
                    
                    # Create enhanced entry
                    create_opponent_attack_entry(
                        attacker=attacker,
                        target=target,
                        attack_roll=attack_roll,
                        damage_roll=damage,
                        hit=True,
                        weapon=getattr(attacker, 'weapon', None)
                    )
                
                # Mark as parsed
                store.parsed_combat_entries.add(entry_id)
                continue
            
            # Pattern: "[NPC Name] misses [Target]!"
            miss_pattern = r"^(.+?)\s+misses\s+(.+?)!"
            miss_match = re.match(miss_pattern, entry)
            
            if miss_match:
                attacker_name = miss_match.group(1).strip()
                target_name = miss_match.group(2).strip()
                
                # Find attacker and target objects
                attacker = None
                target = None
                
                if hasattr(store, 'combat_participants'):
                    for participant in store.combat_participants:
                        if hasattr(participant, 'name'):
                            if participant.name == attacker_name:
                                attacker = participant
                            elif participant.name == target_name:
                                target = participant
                
                if attacker and target:
                    # Estimate attack roll (below AC)
                    import random
                    target_ac = getattr(target, 'ac', 10)
                    attack_roll = max(1, target_ac - random.randint(1, 5))  # Miss by 1-5
                    
                    # Create enhanced entry
                    create_opponent_attack_entry(
                        attacker=attacker,
                        target=target,
                        attack_roll=attack_roll,
                        damage_roll=0,
                        hit=False,
                        weapon=getattr(attacker, 'weapon', None)
                    )
                
                # Mark as parsed
                store.parsed_combat_entries.add(entry_id)

# Styles
style combat_main_frame:
    background "#1a1a1a"
    padding (20, 20)

style combat_stats_frame:
    background "#2a2a2a"
    padding (10, 10)

style combat_actions_frame:
    background "#2a2a2a" 
    padding (10, 10)

style combat_log_frame:
    background "#2a2a2a"
    padding (10, 10)
