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
default selected_action = None
default selected_target = None

# Main combat encounter screen
screen combat_encounter():
    modal True
    
    frame:
        style "combat_main_frame"
        xsize 3800
        ysize 1700
        xalign 0.5
        yalign 0.5
        
        hbox:
            spacing 20
            xfill True
            
            # LEFT PANEL: PARTICIPANT STATS
            frame:
                style "combat_stats_frame"
                xsize 600
                ysize 1500
                
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
                        ysize 1200
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
            
            # CENTER PANEL: COMBAT NARRATIVE AND ACTIONS
            frame:
                style "combat_narrative_frame"
                xsize 2560
                ysize 1500
                
                vbox:
                    spacing 15
                    
                    text "COMBAT NARRATIVE" style "combat_mechanical_text" xalign 0.5
                    
                    # Narrative content viewport
                    viewport:
                        xsize 2560
                        ysize 1000
                        scrollbars "vertical"
                        mousewheel True
                        
                        vbox:
                            spacing 15
                            
                            # Dynamic narrative content will be displayed here
                            if hasattr(store, 'combat_narrative') and store.combat_narrative:
                                for narrative_entry in store.combat_narrative:
                                    frame:
                                        background "#2a2a2a"
                                        padding (15, 15)
                                        xsize 2500
                                        
                                        text "[narrative_entry]" color "#FFFFFF" size 24 text_align 0.0
                            else:
                                # Sample narrative content for testing
                                frame:
                                    background "#2a2a2a"
                                    padding (15, 15)
                                    xsize 2500
                                    
                                    vbox:
                                        spacing 10
                                        text "The rain-slicked alley echoes with the sound of footsteps as combat begins..." color "#FFFFFF" size 24 text_align 0.0
                                
                                frame:
                                    background "#2a2a2a"
                                    padding (15, 15)
                                    xsize 2500
                                    
                                    vbox:
                                        spacing 10
                                        text "Steam rises from the nearby sewer grates, casting eerie shadows on the brick walls. The combatants circle each other warily." color "#FFFFFF" size 24 text_align 0.0
                                
                                frame:
                                    background "#2a2a2a"
                                    padding (15, 15)
                                    xsize 2500
                                    
                                    vbox:
                                        spacing 10
                                        text "Environmental Effects: Wet surfaces may cause slipping. Poor lighting reduces visibility." color "#FFAA00" size 24 text_align 0.0
                    
                    # COMBAT ACTIONS (horizontal layout at bottom)
                    if combat_participants and current_turn_index < len(combat_participants):
                        $ current_participant = combat_participants[current_turn_index]
                        
                        if current_participant == player_stats:
                            text "COMBAT ACTIONS" style "combat_mechanical_text" xalign 0.5
                            
                            frame:
                                background "#333333"
                                padding (10, 10)
                                xsize 2540
                                ysize 350
                                
                                hbox:
                                    spacing 20
                                    xfill True
                                    
                                    # ATTACK ACTIONS
                                    vbox:
                                        spacing 10
                                        xsize 800
                                        
                                        text "ATTACK ACTIONS" color "#00CCFF" size 16 bold True xalign 0.5
                                        
                                        viewport:
                                            xsize 800
                                            ysize 280
                                            scrollbars "vertical"
                                            mousewheel True
                                            
                                            vbox:
                                                spacing 5
                                                
                                                # Weapon attacks
                                                if player_stats.equipped_items:
                                                    for weapon in player_stats.equipped_items:
                                                        if weapon.category == "equippable" and weapon.slot == "weapon":
                                                            button:
                                                                action Function(select_action, {"type": "weapon_attack", "weapon": weapon})
                                                                background "#444444"
                                                                hover_background "#555555"
                                                                padding (8, 5)
                                                                xsize 780
                                                                
                                                                vbox:
                                                                    spacing 2
                                                                    text "[weapon.name]" color "#FFFFFF" size 14 bold True
                                                                    text "Damage: [weapon.effects.get('damage', '1d4')] + STR" color "#CCCCCC" size 11
                                                                    text "Roll: 1d20 + ATK vs Target AC" color "#CCCCCC" size 11
                                                
                                                # Unarmed attack
                                                button:
                                                    action Function(select_action, {"type": "unarmed_attack"})
                                                    background "#444444"
                                                    hover_background "#555555"
                                                    padding (8, 5)
                                                    xsize 780
                                                    
                                                    vbox:
                                                        spacing 2
                                                        text "Unarmed Strike" color "#FFFFFF" size 14 bold True
                                                        text "Damage: 1 + STR" color "#CCCCCC" size 11
                                                        text "Roll: 1d20 + ATK vs Target AC" color "#CCCCCC" size 11
                                    
                                    # DEFENSIVE ACTIONS
                                    vbox:
                                        spacing 10
                                        xsize 800
                                        
                                        text "DEFENSIVE ACTIONS" color "#00CCFF" size 16 bold True xalign 0.5
                                        
                                        viewport:
                                            xsize 800
                                            ysize 280
                                            scrollbars "vertical"
                                            mousewheel True
                                            
                                            vbox:
                                                spacing 5
                                                
                                                button:
                                                    action Function(select_action, {"type": "defend"})
                                                    background "#444444"
                                                    hover_background "#555555"
                                                    padding (8, 5)
                                                    xsize 780
                                                    
                                                    vbox:
                                                        spacing 2
                                                        text "Defend" color "#FFFFFF" size 14 bold True
                                                        text "Effect: +2 AC until next turn" color "#CCCCCC" size 11
                                                        text "Roll: None required" color "#CCCCCC" size 11
                                    
                                    # UTILITY ACTIONS
                                    vbox:
                                        spacing 10
                                        xsize 800
                                        
                                        text "UTILITY ACTIONS" color "#00CCFF" size 16 bold True xalign 0.5
                                        
                                        viewport:
                                            xsize 800
                                            ysize 280
                                            scrollbars "vertical"
                                            mousewheel True
                                            
                                            vbox:
                                                spacing 5
                                                
                                                button:
                                                    action Function(select_action, {"type": "escape"})
                                                    background "#444444"
                                                    hover_background "#555555"
                                                    padding (8, 5)
                                                    xsize 780
                                                    
                                                    vbox:
                                                        spacing 2
                                                        text "Attempt Escape" color "#FFFFFF" size 14 bold True
                                                        text "Effect: Try to flee from combat" color "#CCCCCC" size 11
                                                        text "Roll: 1d20 + DEX vs DC" color "#CCCCCC" size 11
                            
                            # Action confirmation
                            if selected_action:
                                frame:
                                    background "#444444"
                                    padding (10, 10)
                                    xsize 2540
                                    ysize 80
                                    
                                    hbox:
                                        spacing 20
                                        xalign 0.5
                                        
                                        text "SELECT TARGET:" color "#FFFFFF" size 16 bold True
                                        
                                        for participant in combat_participants:
                                            if participant != player_stats:
                                                button:
                                                    action SetVariable("selected_target", participant)
                                                    text "[participant.name]" color "#FFFFFF" size 14
                                                    if selected_target == participant:
                                                        background "#FFD700"
                                                    else:
                                                        background "#666666"
                                                    hover_background "#555555"
                                                    padding (8, 5)
                                        
                                        if selected_target:
                                            textbutton "CONFIRM":
                                                background "#00AA00"
                                                text_color "#FFFFFF"
                                                action Function(confirm_action, selected_action, selected_target)
                                        
                                        textbutton "CANCEL":
                                            background "#AA0000"
                                            text_color "#FFFFFF"
                                            action [SetVariable("selected_action", None), SetVariable("selected_target", None)]
                        else:
                            # NPC turn display
                            text "COMBAT ACTIONS" style "combat_mechanical_text" xalign 0.5
                            
                            frame:
                                background "#333333"
                                padding (20, 20)
                                xsize 2540
                                ysize 350
                                
                                vbox:
                                    spacing 20
                                    xalign 0.5
                                    yalign 0.5
                                    
                                    text "[current_participant.name] is deciding..." color "#FFFF00" size 18
                                    
                                    textbutton "PROCESS NPC TURN":
                                        background "#0066CC"
                                        text_color "#FFFFFF"
                                        action Function(process_npc_turn)

            
            # RIGHT PANEL: COMBAT ACTIONS, ROLL INTERFACE & MECHANICAL LOG
            frame:
                style "combat_log_frame"
                xsize 600
                ysize 1500
                xalign 1.0
                
                vbox:
                    spacing 15
                    
                    # Roll interface
                    frame:
                        background "#333333"
                        padding (10, 10)
                        xsize 580
                        ysize 430
                        
                        vbox:
                            spacing 10
                            
                            text "DICE ROLL" style "combat_mechanical_text" xalign 0.5
                            
                            if pending_roll:
                                $ action_data = pending_roll["action"]
                                $ target = pending_roll["target"]
                                
                                text "PENDING:" color "#00FF00" size 16 bold True
                                
                                if action_data["type"] == "weapon_attack":
                                    $ weapon = action_data["weapon"]
                                    text "Attack: [weapon.name]" style "combat_mechanical_text_sub1"
                                    if target:
                                        text "Target: [target.name] (AC [target.ac])" style "combat_mechanical_text_sub1"
                                elif action_data["type"] == "unarmed_attack":
                                    text "Unarmed Strike" style "combat_mechanical_text_sub1"
                                    if target:
                                        text "Target: [target.name] (AC [target.ac])" style "combat_mechanical_text_sub1"
                                elif action_data["type"] == "escape":
                                    text "Escape Attempt" style "combat_mechanical_text_sub1"
                                
                                hbox:
                                    spacing 20
                                    xalign 0.5
                                    
                                    textbutton "ROLL D20":
                                        background "#00AA00"
                                        text_color "#FFFFFF"
                                        text_size 16
                                        action Function(execute_roll, pending_roll)
                                    
                                    textbutton "CANCEL":
                                        background "#AA0000"
                                        text_color "#FFFFFF"
                                        action SetVariable("pending_roll", None)
                            
                            else:
                                text "No pending roll" color "#CCCCCC" size 24 xalign 0.5
                    
                    # Combat log
                    frame:
                        background "#333333"
                        padding (10, 10)
                        xsize 580
                        ysize 430
                        
                        vbox:
                            spacing 10
                            
                            text "COMBAT LOG" style "combat_mechanical_text" xalign 0.5
                            
                            viewport:
                                xsize 560
                                ysize 400
                                scrollbars "vertical"
                                mousewheel True
                                
                                vbox:
                                    spacing 8
                                    
                                    if combat_log:
                                        for log_entry in combat_log:
                                            text "[log_entry]" color "#FFFFFF" size 24
                                    else:
                                        text "Combat begins..." color "#CCCCCC" size 24
                    
                   
                vbox:
                    spacing 15
                    
                    # Roll interface
                    frame:
                        background "#333333"
                        padding (10, 10)
                        xsize 580
                        ysize 430
                        
                        vbox:
                            spacing 10
                            
                            text "DICE ROLL" style "combat_mechanical_text" xalign 0.5
                            
                            if pending_roll:
                                $ action_data = pending_roll["action"]
                                $ target = pending_roll["target"]
                                
                                text "PENDING:" color "#00FF00" size 16 bold True
                                
                                if action_data["type"] == "weapon_attack":
                                    $ weapon = action_data["weapon"]
                                    text "Attack: [weapon.name]" style "combat_mechanical_text_sub1"
                                    if target:
                                        text "Target: [target.name] (AC [target.ac])" style "combat_mechanical_text_sub1"
                                elif action_data["type"] == "unarmed_attack":
                                    text "Unarmed Strike" style "combat_mechanical_text_sub1"
                                    if target:
                                        text "Target: [target.name] (AC [target.ac])" style "combat_mechanical_text_sub1"
                                elif action_data["type"] == "escape":
                                    text "Escape Attempt" style "combat_mechanical_text_sub1"
                                
                                hbox:
                                    spacing 20
                                    xalign 0.5
                                    
                                    textbutton "ROLL D20":
                                        background "#00AA00"
                                        text_color "#FFFFFF"
                                        text_size 16
                                        action Function(execute_roll, pending_roll)
                                    
                                    textbutton "CANCEL":
                                        background "#AA0000"
                                        text_color "#FFFFFF"
                                        action SetVariable("pending_roll", None)
                            
                            else:
                                text "No pending roll" color "#CCCCCC" size 24 xalign 0.5
                    
                    # Combat log
                    frame:
                        background "#333333"
                        padding (10, 10)
                        xsize 580
                        ysize 800
                        
                        vbox:
                            spacing 10
                            
                            text "COMBAT LOG" style "combat_mechanical_text" xalign 0.5
                            
                            viewport:
                                xsize 560
                                ysize 400
                                scrollbars "vertical"
                                mousewheel True
                                
                                vbox:
                                    spacing 8
                                    
                                    if combat_log:
                                        for log_entry in combat_log:
                                            text "[log_entry]" color "#FFFFFF" size 24
                                    else:
                                        text "Combat begins..." color "#CCCCCC" size 24

        
        # Vertical control buttons with hover effects
        hbox:
            xpos 7
            ypos 1425
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
    def handle_end_turn():
        """Handle end turn button logic"""
        if not combat_participants or current_turn_index >= len(combat_participants):
            return
        
        current_participant = combat_participants[current_turn_index]
        if current_participant == player_stats:
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
            attack_total = d20_result + player_stats.atk_bonus + str_mod
            
            combat_log.append(f"Roll: {d20_result} + {player_stats.atk_bonus + str_mod} = {attack_total}")
            
            if d20_result == 1:
                combat_log.append("CRITICAL FAILURE!")
            elif attack_total >= target.ac:
                if action_data["type"] == "weapon_attack":
                    weapon = action_data["weapon"]
                    damage = roll_damage_dice(weapon.effects.get("damage", "1d4")) + str_mod
                else:
                    damage = 1 + str_mod
                
                damage = max(1, damage)
                target.hp = max(0, target.hp - damage)
                
                if d20_result == 20:
                    combat_log.append(f"CRITICAL HIT! {damage} damage to {target.name}!")
                else:
                    combat_log.append(f"Hit! {damage} damage to {target.name}!")
            else:
                combat_log.append(f"Miss! Attack vs {target.name} fails.")
        
        store.pending_roll = None
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
    
    def confirm_action(action_data, target):
        """Confirm the selected action against the target"""
        global pending_roll, selected_action, selected_target
        
        # Set up the pending roll with the action and target
        pending_roll = {
            "action": action_data,
            "target": target
        }
        
        # Reset the selection variables
        selected_action = None
        selected_target = None
        
        # Add a message to the combat log
        combat_log.append(f"{player_stats.name} targets {target.name}")
    
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
