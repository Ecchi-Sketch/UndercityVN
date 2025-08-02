#============================================================================
# COMBAT ENCOUNTER GUI SYSTEM (Refactored for Manual Input with Bonus Breakdown)
#============================================================================

init python:
    # This variable will store the text entered by the user for their roll.
    manual_roll_input = ""

    def get_player_bonuses_and_effects():
        """
        Calculates and breaks down the applicable bonuses and active effects for the player's current action.
        Returns a list of bonus components, the total bonus value, and a list of active effect strings.
        """
        combat_manager = get_combat_manager()
        if not combat_manager:
            return [], 0, []

        # For initiative rolls, we need to find the player combatant specifically
        # rather than the current combatant (which might not be set yet)
        if combat_manager.combat_state == 'awaiting_initiative_roll':
            for combatant in combat_manager.pending_initiative_rolls:
                if getattr(combatant.character_data, 'is_player', False):
                    actor = combatant
                    break
        else:
            # For other rolls, use current combatant
            actor = combat_manager.get_current_combatant()
            
        if not actor or not actor.character_data.is_player:
            return [], 0, []

        bonus_components = []
        total_bonus = 0
        active_effects = []

        # Gather active effects from equipped items
        for item in actor.character_data.equipped_items:
            effect_strings = []
            for effect, value in item.effects.items():
                if "damage" not in effect: # Don't show the base damage die as an effect
                    effect_strings.append("{}: +{}".format(effect.replace("_", " ").title(), value))
            if effect_strings:
                active_effects.append("{}: {}".format(item.name, ", ".join(effect_strings)))
        
        # Gather active effects from skills
        for skill_id in actor.character_data.active_skills:
            if skill_id in skill_database:
                skill = skill_database[skill_id]
                level = actor.character_data.learned_skills.get(skill_id, 1)
                
                # Simplified effect string generation for skills
                effect_strings = []
                for effect, base_value in skill.base_effects.items():
                    per_level_value = skill.per_level_effects.get(effect, 0)
                    total_skill_bonus = base_value + (per_level_value * (level - 1))
                    effect_strings.append("{}: +{}".format(effect.replace("_", " ").title(), total_skill_bonus))
                
                if effect_strings:
                    active_effects.append("{}: {}".format(skill.name, ", ".join(effect_strings)))


        # Determine bonus for an INITIATIVE roll
        if combat_manager.combat_state == 'awaiting_initiative_roll':
            dex_mod = get_ability_modifier(actor.character_data.dexterity)
            bonus_components.append(("Dexterity Bonus", dex_mod))
            
            total_bonus = dex_mod
            return bonus_components, total_bonus, active_effects
        
        # Determine bonus for an ATTACK roll
        elif combat_manager.combat_state == 'awaiting_player_roll':
            ability_mod = get_ability_modifier(actor.character_data.strength)
            bonus_components.append(("Strength Bonus", ability_mod))

            prof_bonus = actor.character_data.proficiency_bonus
            bonus_components.append(("Proficiency Bonus", prof_bonus))

            other_bonuses = actor.character_data.atk_bonus
            if other_bonuses != 0:
                bonus_components.append(("Other Bonuses (Skills/Items)", other_bonuses))

            # Check for advantage/disadvantage
            roll_type = actor.get_attack_roll_type()
            if roll_type == "advantage":
                active_effects.append("{color=#ffff00}ADVANTAGE: Roll twice, use higher result{/color}")
            elif roll_type == "disadvantage":
                active_effects.append("{color=#ff8080}DISADVANTAGE: Roll twice, use lower result{/color}")

            total_bonus = ability_mod + prof_bonus + other_bonuses
            return bonus_components, total_bonus, active_effects
        
        # Determine bonus for a DAMAGE roll
        elif combat_manager.combat_state == 'awaiting_damage_roll':
            ability_mod = get_ability_modifier(actor.character_data.strength)
            bonus_components.append(("Strength Bonus", ability_mod))
            
            other_bonuses = actor.character_data.dmg_bonus
            if other_bonuses != 0:
                bonus_components.append(("Other Bonuses (Skills/Items)", other_bonuses))

            total_bonus = ability_mod + other_bonuses
            return bonus_components, total_bonus, active_effects

        return [], 0, []


    def ui_select_attack_action():
        combat_manager = get_combat_manager()
        if not combat_manager or combat_manager.combat_state != 'active': return
        actor = combat_manager.get_current_combatant()
        target = next((p for p in combat_manager.turn_order if p.id != actor.id and not p.is_defeated()), None)
        if not target: return
        weapon = next((item for item in actor.character_data.equipped_items if item.slot == 'weapon'), None)
        if not weapon: return
        
        combat_manager.combat_state = 'awaiting_player_roll'
        combat_manager.pending_action = {"type": "attack", "actor": actor, "target": target, "weapon": weapon}
        prompt_message = "Player, attack {}.".format(target.get_name())
        combat_manager._log_event({"event_type": "prompt", "message": prompt_message})

    def ui_select_defend_action():
        """Handle defend button - show available defensive skills"""
        combat_manager = get_combat_manager()
        if not combat_manager or combat_manager.combat_state != 'active': return
        actor = combat_manager.get_current_combatant()
        if not actor or not actor.character_data.is_player: return
        
        # Check available defensive skills
        defensive_skills = []
        if "dodge" in actor.character_data.learned_skills:
            defensive_skills.append("dodge")
        if "block" in actor.character_data.learned_skills:
            defensive_skills.append("block")
        
        if not defensive_skills:
            # Basic defend action if no skills available
            combat_manager._log_event({
                "event_type": "defend_action", 
                "actor": actor.get_name(),
                "message": "{} takes a basic defensive stance.".format(actor.get_name())
            })
            # Mark action as taken and advance turn properly
            actor.action_taken = True
            # Reset combat state to active
            combat_manager.combat_state = 'active'
            combat_manager.advance_turn()
        else:
            # Set combat state to show defend menu
            combat_manager.combat_state = 'awaiting_defend_choice'
            combat_manager.available_defend_skills = defensive_skills

    def ui_select_dodge_action():
        combat_manager = get_combat_manager()
        if not combat_manager or combat_manager.combat_state not in ['active', 'awaiting_defend_choice']: return
        actor = combat_manager.get_current_combatant()
        if not actor or not actor.character_data.is_player: return
        
        # Check if player has dodge skill
        if "dodge" not in actor.character_data.learned_skills:
            combat_manager._log_event({"event_type": "action_failed", "message": "You don't know how to dodge effectively."})
            return
            
        # Apply disadvantage to all opponents for their next attack
        opponents_affected = []
        for combatant in combat_manager.turn_order:
            if combatant.id != actor.id and not combatant.is_defeated():
                combatant.add_status_effect("disadvantage_next_attack", 1)
                opponents_affected.append(combatant.get_name())
        
        # Log disadvantage application
        if opponents_affected:
            combat_manager._log_event({
                "event_type": "status_effect_applied",
                "message": "Disadvantage applied to: {}".format(", ".join(opponents_affected))
            })
        
        # Log the dodge action
        combat_manager._log_event({
            "event_type": "dodge_action", 
            "actor": actor.get_name(),
            "message": "{} takes a defensive stance, making them harder to hit.".format(actor.get_name())
        })
        
        # Mark action as taken and end player's turn
        actor.action_taken = True
        # Reset combat state to active
        combat_manager.combat_state = 'active'
        combat_manager.advance_turn()

    def ui_select_block_action():
        combat_manager = get_combat_manager()
        if not combat_manager or combat_manager.combat_state not in ['active', 'awaiting_defend_choice']: return
        actor = combat_manager.get_current_combatant()
        if not actor or not actor.character_data.is_player: return
        
        # Check if player has block skill
        if "block" not in actor.character_data.learned_skills:
            combat_manager._log_event({"event_type": "action_failed", "message": "You don't know how to block effectively."})
            return
        
        # Calculate block percentage: block_level * ((constitution - 10) // 2)
        block_level = actor.character_data.learned_skills["block"]
        con_modifier = (actor.character_data.constitution - 10) // 2
        block_percentage = block_level * con_modifier
        
        # Ensure block percentage is at least 0
        block_percentage = max(0, block_percentage)
        
        # Apply block effect to player for next incoming attack
        actor.add_status_effect("block_next_attack", 1)
        # Store the block percentage as a custom attribute
        actor.block_percentage = block_percentage
        
        # Log the block action
        combat_manager._log_event({
            "event_type": "block_action", 
            "actor": actor.get_name(),
            "message": "{} raises their guard, reducing the next attack by {}%.".format(actor.get_name(), block_percentage)
        })
        
        # Mark action as taken and end player's turn
        actor.action_taken = True
        # Reset combat state to active
        combat_manager.combat_state = 'active'
        combat_manager.advance_turn()

    def ui_cancel_defend_menu():
        """Cancel defend menu and return to normal combat state"""
        combat_manager = get_combat_manager()
        if not combat_manager: return
        
        # Return to active combat state
        combat_manager.combat_state = 'active'
        if hasattr(combat_manager, 'available_defend_skills'):
            delattr(combat_manager, 'available_defend_skills')

    def ui_process_player_d20_roll(total_attack_roll, roll_type=None):
        combat_manager = get_combat_manager()
        if not combat_manager or combat_manager.combat_state != 'awaiting_player_roll': return
        pending = combat_manager.pending_action
        if pending and pending["type"] == "attack":
            combat_manager.resolve_attack(
                actor=pending["actor"],
                target=pending["target"],
                weapon=pending["weapon"],
                total_attack_roll=total_attack_roll,
                roll_type=roll_type
            )

    def ui_process_player_damage_roll(total_damage):
        combat_manager = get_combat_manager()
        if not combat_manager or combat_manager.combat_state != 'awaiting_damage_roll': return
        pending = combat_manager.pending_action
        if pending and pending["type"] == "attack":
            combat_manager.resolve_damage(
                actor=pending["actor"],
                target=pending["target"],
                weapon=pending["weapon"],
                total_damage=total_damage,
                is_critical=pending.get("is_critical", False)
            )
            combat_manager.pending_action = None

    def ui_process_player_initiative_roll(total_initiative_roll):
        combat_manager = get_combat_manager()
        if not combat_manager or combat_manager.combat_state != 'awaiting_initiative_roll': return
        combat_manager.process_player_initiative_roll(total_initiative_roll)

    def ui_resolve_finishing_blow(choice):
        combat_manager = get_combat_manager()
        if not combat_manager or combat_manager.combat_state != 'awaiting_finishing_blow': return
        combat_manager.resolve_finishing_blow(choice)

    def submit_manual_roll(roll_type=None):
        global manual_roll_input
        combat_manager = get_combat_manager()
        if not combat_manager: return

        try:
            roll_value = int(manual_roll_input)
            
            if combat_manager.combat_state == 'awaiting_initiative_roll':
                combat_manager.process_player_initiative_roll(roll_value)
            elif combat_manager.combat_state == 'awaiting_player_roll':
                ui_process_player_d20_roll(roll_value, roll_type)
            elif combat_manager.combat_state == 'awaiting_damage_roll':
                ui_process_player_damage_roll(roll_value)
            
            manual_roll_input = ""
            renpy.restart_interaction()

        except (ValueError, TypeError):
            manual_roll_input = ""
            renpy.restart_interaction()

    def ui_proceed_opponent_action():
        """Manually trigger opponent action when proceed button is pressed"""
        combat_manager = get_combat_manager()
        if not combat_manager or combat_manager.combat_state != 'active': 
            return
        
        current_combatant = combat_manager.get_current_combatant()
        if current_combatant and not getattr(current_combatant.character_data, 'is_player', False):
            # Manually trigger the opponent's action
            combat_manager._process_npc_turn_manual()
            renpy.restart_interaction()

    def ui_resolve_pending_attack():
        """Handle second proceed button to resolve the announced attack"""
        combat_manager = get_combat_manager()
        if combat_manager:
            combat_manager._resolve_pending_attack()
    
    def ui_proceed_after_opponent_action():
        """Handle third proceed button after opponent action completes"""
        combat_manager = get_combat_manager()
        if combat_manager:
            combat_manager._proceed_after_opponent_action()
    
    def ui_burn_grit_point():
        """Handle burning a grit point for an additional action during opponent's turn"""
        combat_manager = get_combat_manager()
        if not combat_manager:
            return
        
        # Check if player can spend grit
        if player_stats.spend_grit_point():
            # Log the grit expenditure
            combat_manager._log_event({
                "event_type": "grit_spent",
                "message": "Player burns a grit point for an additional action! ({} remaining)".format(player_stats.grit_points),
                "grit_remaining": player_stats.grit_points
            })
            
            # Set combat state to allow player action
            combat_manager.combat_state = 'active'
            
            # Give the player their turn back
            for i, combatant in enumerate(combat_manager.turn_order):
                if getattr(combatant.character_data, 'is_player', False):
                    combat_manager.current_turn_index = i
                    break
            
            renpy.restart_interaction()
        else:
            renpy.notify("No grit points available!")


screen combat_encounter():
    modal True
    
    $ combat_manager = get_combat_manager()

    frame:
        style "combat_main_frame"
        xsize 3850
        ysize 1720
        xalign 0.5
        yalign 0.5
        
        if combat_manager:
            hbox:
                spacing 20
                xfill True
                
                # --- LEFT PANEL: PARTICIPANT STATS (Unchanged) ---
                frame:
                    style "combat_stats_frame"
                    xsize 600
                    ysize 1675
                    vbox:
                        spacing 10
                        frame:
                            xsize 580
                            background "#333333"
                            padding (10, 10)
                            vbox:
                                spacing 5
                                text "ROUND [combat_manager.round_number]" color "#FFD700" size 24 bold True
                                $ current_combatant = combat_manager.get_current_combatant()
                                if current_combatant:
                                    text "[current_combatant.get_name()]'S TURN" style "combat_mechanical_text"
                                text "INITIATIVE ORDER:" style "combat_mechanical_text_sub1"
                                for i, participant in enumerate(combat_manager.turn_order):
                                    $ is_current = (i == combat_manager.current_turn_index)
                                    $ status_color = "#FFD700" if is_current else "#FFFFFF"
                                    hbox:
                                        spacing 10
                                        if is_current:
                                            text "►" color "#FFD700" size 20
                                        else:
                                            text " " size 20
                                        text "[participant.get_name()]" color status_color size 18
                        viewport:
                            xsize 580
                            ysize 1375
                            scrollbars "vertical"
                            mousewheel True
                            vbox:
                                spacing 15
                                for participant in combat_manager.turn_order:
                                    frame:
                                        background "#333333"
                                        padding (10, 10)
                                        xalign 0.5
                                        xsize 560
                                        vbox:
                                            spacing 8
                                            hbox:
                                                spacing 10
                                                text "[participant.get_name()]" color "#FFFFFF" size 20 bold True
                                                if getattr(participant.character_data, 'is_player', False):
                                                    text "(YOU)" color "#00FF00" size 14
                                            $ hp_percent = float(participant.current_hp) / float(participant.character_data.max_hp) if participant.character_data.max_hp > 0 else 0
                                            $ hp_color = "#00FF00" if hp_percent > 0.6 else "#FFFF00" if hp_percent > 0.3 else "#FF0000"
                                            hbox:
                                                spacing 5
                                                text "HP:" style "combat_stats_text"
                                                bar:
                                                    value participant.current_hp
                                                    range participant.character_data.max_hp
                                                    xsize 200
                                                    ysize 20
                                                    left_bar hp_color
                                                    right_bar "#333333"
                                                text "[participant.current_hp]/[participant.character_data.max_hp]" color "#FFFFFF" size 24
                                            grid 2 4:
                                                spacing 5
                                                text "AC:" style "combat_stats_text"
                                                text "[participant.get_ac()]" style "combat_mechanical_text_sub1"
                                                text "ATK:" style "combat_stats_text"
                                                text "+[participant.character_data.atk_bonus]" style "combat_mechanical_text_sub1"
                                                text "DMG:" style "combat_stats_text"
                                                text "+[participant.character_data.dmg_bonus]" style "combat_mechanical_text_sub1"
                                                text "PROF:" style "combat_stats_text"
                                                text "+[participant.character_data.proficiency_bonus]" style "combat_mechanical_text_sub1"
                                            if participant.status_effects:
                                                text "STATUS:" color "#FF6600" size 24 bold True
                                                for effect in participant.status_effects:
                                                    $ effect_name = effect['name']
                                                    $ display_name = effect_name
                                                    if effect_name == "disadvantage_next_attack":
                                                        $ display_name = "Disadvantage on Next Attack"
                                                    elif effect_name == "advantage_next_attack":
                                                        $ display_name = "Advantage on Next Attack"
                                                    elif effect_name == "block_next_attack":
                                                        $ display_name = "Block Ready"
                                                    text "• [display_name] ([effect['duration']])" color "#FFAA66" size 24
                
                # --- CENTER PANEL: LOGS (Unchanged) ---
                vbox:
                    spacing 20
                    xsize 2560
                    frame:
                        style "combat_log_frame"
                        xsize 2500
                        ysize 828
                        vbox:
                            spacing 10
                            text "NARRATIVE LOG" style "combat_mechanical_text" xalign 0.5
                            viewport:
                                id "narrative_log_vp"
                                xsize 2540
                                ysize 778
                                scrollbars "vertical"
                                mousewheel True
                                yinitial 1.0
                                vbox:
                                    spacing 10
                                    if combat_manager.narrative_log:
                                        # Show newest messages at the top with color fading
                                        $ reversed_log = list(reversed(combat_manager.narrative_log))
                                        for i, entry in enumerate(reversed_log):
                                            # Simple two-color system: white for newest, grey for older
                                            $ entry_color = "#FFFFFF" if i == 0 else "#888888"
                                            text "[entry]" style "log_body_text" color entry_color
                                    else:
                                        text "Narrative descriptions will appear here..." color "#888888" size 20 italic True xalign 0.5
                    frame:
                        style "combat_log_frame"
                        xsize 2500
                        ysize 827
                        vbox:
                            spacing 10
                            text "COMBAT LOG (MECHANICAL)" style "combat_mechanical_text" xalign 0.5
                            viewport:
                                id "mechanical_log_vp"
                                xsize 2540
                                ysize 777
                                scrollbars "vertical"
                                mousewheel True
                                yinitial 1.0
                                vbox:
                                    spacing 10
                                    if combat_manager.mechanical_log:
                                        # Show newest messages at the top with color fading
                                        $ reversed_mech_log = list(reversed(combat_manager.mechanical_log))
                                        for i, log_entry in enumerate(reversed_mech_log):
                                            # Simple two-color system: white for newest, grey for older
                                            $ entry_color = "#FFFFFF" if i == 0 else "#888888"
                                            $ formatted_text = format_mechanical_log_entry(log_entry)
                                            text "[formatted_text]" style "log_body_text" color entry_color
                                    else:
                                        text "Mechanical details will appear here..." color "#888888" size 20 italic True xalign 0.5
                
                # --- RIGHT PANEL: MANUAL ROLL INPUT (Redesigned with Active Effects) ---
                frame:
                    style "combat_log_frame"
                    xsize 600
                    ysize 1675
                    xalign 0.0
                    
                    vbox:
                        xalign 0.5
                        yalign 0.5
                        spacing 15

                        if combat_manager.combat_state in ['awaiting_player_roll', 'awaiting_damage_roll', 'awaiting_initiative_roll']:
                            
                            $ bonus_components, total_bonus, active_effects = get_player_bonuses_and_effects()
                            
                            if bonus_components:
                                text "Your Bonuses:" style "combat_mechanical_text" xalign .5
                                frame:
                                    background "#1a1a1a"
                                    padding (10, 10)
                                    xalign 0.5
                                    vbox:
                                        xsize 500
                                        spacing 5
                                        xalign 1.0
                                        for name, value in bonus_components:
                                            hbox:
                                                text name style "combat_bonus_text"
                                                xfill False
                                                text "+ [value]" style "combat_bonus_text" xalign 0.5 color "#00FF00"
                                
                                text "Total Bonus:" size 24 color "#FFFFFF" xalign 0.5
                                text "+ [total_bonus]" size 36 color "#00FF00" xalign 0.5 bold True
                            
                            # Show equipped items and their damage dice (only during damage rolls)
                            if combat_manager.combat_state == 'awaiting_damage_roll':
                                $ actor = combat_manager.get_current_combatant()
                                $ equipped_items = [item for item in actor.character_data.equipped_items if hasattr(item, 'effects') and any('damage' in effect for effect in item.effects.keys())] if actor else []
                                if equipped_items:
                                    text "Equipped Weapon Damage:" size 24 color "#FFFFFF" xalign 0.5
                                    frame:
                                        background "#1a1a1a"
                                        padding (10, 10)
                                        xalign 0.5
                                        vbox:
                                            xsize 400
                                            spacing 5
                                            $ damage_dice = []
                                            $ dice_counts = {}
                                            for item in equipped_items:
                                                for effect, value in item.effects.items():
                                                    if 'damage' in effect:
                                                        $ damage_dice.append(value)
                                                        $ dice_counts[value] = dice_counts.get(value, 0) + 1
                                                        text "[item.name]: [value]" style "combat_bonus_text" xalign 0.5
                                            if damage_dice:
                                                $ combined_dice = []
                                                for die_type, count in sorted(dice_counts.items()):
                                                    if count == 1:
                                                        $ combined_dice.append(die_type)
                                                    else:
                                                        # Extract just the die part (e.g., "d4" from "1d4")
                                                        $ die_part = die_type[1:] if die_type.startswith('1') else die_type
                                                        $ combined_dice.append(str(count) + die_part)
                                                text "Total Damage Dice: "  style "combat_bonus_text" xalign 0.5 color "#00FF00"
                                                text "[' + '.join(combined_dice)]"  style "combat_bonus_text" xalign 0.5 color "#00FF00"

                            # MODIFIED: Prompt now changes based on combat state.
                            if combat_manager.combat_state == 'awaiting_initiative_roll':
                                $ final_prompt = "INITIATIVE ROLL: Roll a d20, add your bonus of +{}, and enter the TOTAL.".format(total_bonus)
                            elif combat_manager.combat_state == 'awaiting_damage_roll' and combat_manager.pending_action.get("is_critical", False):
                                $ final_prompt = "CRITICAL HIT! Roll DOUBLE damage dice, add your bonus of +{}, and enter the TOTAL.".format(total_bonus)
                            else:
                                $ final_prompt = "Roll your dice, add your bonus of +{}, and enter the TOTAL.".format(total_bonus)
                            
                            text "[final_prompt]" size 24 color "#FFD700" xalign 0.5

                            input value VariableInputValue("manual_roll_input") length 3 allow "0123456789" style "input" text_align 0.5 size 40 xalign 0.5

                            if combat_manager.combat_state == 'awaiting_player_roll':
                                vbox:
                                    xalign 0.5
                                    spacing 15
                                    add Solid("#404040", xfill=True, ysize=1)
                                    textbutton "Submit Total" action Function(submit_manual_roll) text_style "green_to_blue"  xalign 0.5
                                    text "Submit using buttons below if dice roll was nat 1 or 20" style "inactive_text" xalign 0.5 bold True
                                    textbutton "Nat 20" action Function(submit_manual_roll, "nat20") text_style "white_to_blue"  xalign 0.5
                                    textbutton "Nat 1" action Function(submit_manual_roll, "nat1") text_style "white_to_blue"  xalign 0.5
                            else:
                                textbutton "Submit Total" action Function(submit_manual_roll) xalign 0.5  text_style "green_to_blue"
                        
                        else:
                            # Show proceed button when it's opponent's turn
                            $ current_combatant = combat_manager.get_current_combatant()
                            $ is_opponent_turn = current_combatant and not getattr(current_combatant.character_data, 'is_player', False)
                            
                            if is_opponent_turn and combat_manager.combat_state == 'active':
                                vbox:
                                    spacing 20
                                    xalign 0.5
                                    text "Opponent's Turn" size 24 color "#FFD700" xalign 0.5
                                    text "[current_combatant.get_name()] is ready to act" size 18 color "#CCCCCC" xalign 0.5
                                    
                                    # Show both proceed and grit buttons
                                    hbox:
                                        spacing 20
                                        xalign 0.5
                                        textbutton "PROCEED" action Function(ui_proceed_opponent_action) text_style "green_to_blue" text_size 20 xsize 150 ysize 50
                                        
                                        # Only show grit button if player has grit points available
                                        if player_stats.grit_points > 0:
                                            textbutton "Burn Grit Pt: [player_stats.grit_points] remaining" action Function(ui_burn_grit_point) text_style "red_white_highlight_text" text_size 16 xsize 200 ysize 50
                            elif combat_manager.combat_state == 'awaiting_attack_resolution':
                                vbox:
                                    spacing 20
                                    xalign 0.5
                                    text "Attack Announced" size 24 color "#FFD700" xalign 0.5
                                    text "Click to see the results" size 18 color "#CCCCCC" xalign 0.5
                                    textbutton "PROCEED" action Function(ui_resolve_pending_attack) text_style "green_to_blue" xalign 0.5 text_size 20 xsize 150 ysize 50
                            elif combat_manager.combat_state == 'awaiting_post_action_proceed':
                                vbox:
                                    spacing 20
                                    xalign 0.5
                                    text "Action Complete" size 24 color "#FFD700" xalign 0.5
                                    text "Review the results above" size 18 color "#CCCCCC" xalign 0.5
                                    textbutton "PROCEED" action Function(ui_proceed_after_opponent_action) text_style "green_to_blue" xalign 0.5 text_size 20 xsize 150 ysize 50
                            else:
                                text "Awaiting combat action..." size 22 color "#888888" xalign 0.5
            
            # --- FINISHING BLOW OVERLAY (Unchanged) ---
            if combat_manager.combat_state == 'awaiting_finishing_blow':
                frame:
                    background "#000000a0"
                    xfill True
                    yfill True
                    vbox:
                        xalign 0.5 yalign 0.5 spacing 20
                        text "Deliver a Finishing Blow?" style "subheader_text" size 40
                        hbox:
                            spacing 50
                            textbutton "Lethal" action Function(ui_resolve_finishing_blow, "lethal")
                            textbutton "Non-Lethal" action Function(ui_resolve_finishing_blow, "nonlethal")

            # --- BOTTOM PANEL: ACTION BUTTONS (Unchanged) ---
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
                    hbox:
                        spacing 40
                        xalign 0.5
                        yalign 0.5
                        $ current_combatant = combat_manager.get_current_combatant()
                        $ can_act = (current_combatant and current_combatant.character_data == player_stats and combat_manager.combat_state == 'active')
                        if combat_manager.combat_state == 'awaiting_defend_choice':
                            # Show defend skill menu
                            text "Choose Defensive Action:" color "#FFFFFF" size 24 bold True xalign 0.5
                            null height 20
                            vbox:
                                spacing 15
                                xalign 0.5
                                for skill in combat_manager.available_defend_skills:
                                    if skill == "dodge":
                                        textbutton "DODGE" background "#0066AA" hover_background "#3388CC" text_color "#FFFFFF" text_hover_color "#FFFF00" text_size 20 xsize 180 ysize 50 action Function(ui_select_dodge_action)
                                    elif skill == "block":
                                        textbutton "BLOCK" background "#0066AA" hover_background "#3388CC" text_color "#FFFFFF" text_hover_color "#FFFF00" text_size 20 xsize 180 ysize 50 action Function(ui_select_block_action)
                                textbutton "CANCEL" background "#666666" hover_background "#888888" text_color "#FFFFFF" text_hover_color "#FFFF00" text_size 20 xsize 180 ysize 50 action Function(ui_cancel_defend_menu)
                        else:
                            # Show normal combat actions
                            textbutton "ATTACK" background "#AA0000" hover_background "#CC3333" text_color "#FFFFFF" text_hover_color "#FFFF00" text_size 24 xsize 200 ysize 60 action Function(ui_select_attack_action) sensitive can_act
                            textbutton "DEFEND" background "#0066AA" hover_background "#3388CC" text_color "#FFFFFF" text_hover_color "#FFFF00" text_size 24 xsize 200 ysize 60 action Function(ui_select_defend_action) sensitive can_act
                            textbutton "UTILITY" background "#6600AA" hover_background "#8833CC" text_color "#FFFFFF" text_hover_color "#FFFF00" text_size 24 xsize 200 ysize 60 action NullAction() sensitive can_act
                            textbutton "ITEM" background "#AA6600" hover_background "#CC8833" text_color "#FFFFFF" text_hover_color "#FFFF00" text_size 24 xsize 200 ysize 60 action NullAction() sensitive can_act
            
            # --- Vertical control buttons (Unchanged) ---
            hbox:
                xpos 7
                ypos 1600
                spacing 30
                textbutton "END TURN" background "#666666" hover_background "#888888" text_color "#FFFFFF" text_hover_color "#FFFF00" text_size 22 xsize 175 ysize 50 action NullAction() sensitive can_act
                textbutton "FLEE COMBAT" background "#AA0000" hover_background "#CC3333" text_color "#FFFFFF" text_hover_color "#FFFF00" text_size 22 xsize 180 ysize 50 action NullAction() sensitive can_act
                textbutton "EXIT COMBAT" background "#333333" hover_background "#555555" text_color "#FFFFFF" text_hover_color "#FFFF00" text_size 22 xsize 175 ysize 50 action Return()

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
