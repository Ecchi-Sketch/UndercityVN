#============================================================================
# ENHANCED DICE ROLL INTERFACE SYSTEM (Updated for Combat Integration)
#============================================================================

python early:
    import time
    
    class DiceRollRequest:
        def __init__(self, dice_type="d20", modifier=0, context="general", advantage=False, disadvantage=False, label="Roll"):
            self.dice_type, self.modifier, self.context, self.advantage, self.disadvantage, self.label, self.timestamp = dice_type, modifier, context, advantage, disadvantage, label, time.time()
    
    class DiceRollResult:
        def __init__(self, roll_request, raw_rolls, final_result, chosen_roll=None):
            self.request, self.raw_rolls, self.final_result, self.chosen_roll, self.timestamp = roll_request, raw_rolls, final_result, chosen_roll, time.time()
            
        def format_display(self):
            # This now displays the raw roll + modifier from the request, which is 0 for combat rolls
            # but allows the dice roller to still be used for other checks with modifiers.
            if self.request.advantage or self.request.disadvantage:
                adv_text = "ADV" if self.request.advantage else "DIS"
                chosen_roll_display = self.chosen_roll if self.chosen_roll is not None else 0
                return "{} ({}) [{}:{}] {}{}= {}".format(self.request.dice_type, ','.join(map(str, self.raw_rolls)), adv_text, chosen_roll_display, '+' if self.request.modifier >= 0 else '', self.request.modifier, self.final_result)
            else:
                roll_str = str(self.raw_rolls[0]) if len(self.raw_rolls) == 1 else "+".join(map(str, self.raw_rolls))
                if self.request.modifier != 0:
                    return "{} ({}) {}{}= {}".format(self.request.dice_type, roll_str, '+' if self.request.modifier >= 0 else '', self.request.modifier, self.final_result)
                else:
                    return "{} ({})= {}".format(self.request.dice_type, roll_str, self.final_result)

init python:
    def queue_dice_roll(dice_type="d20", modifier=0, context="general", advantage=False, disadvantage=False, label="Roll"):
        global pending_dice_roll
        pending_dice_roll = DiceRollRequest(dice_type, modifier, context, advantage, disadvantage, label)
        
    def execute_dice_roll():
        global pending_dice_roll, last_roll_result, roll_history, dice_animation_playing
        if not pending_dice_roll: return None
        
        dice_animation_playing = True
        renpy.timeout(0.1)

        dice_str = pending_dice_roll.dice_type
        try:
            if 'd' in dice_str:
                count, sides = map(int, dice_str.split('d'))
            else:
                count, sides = 1, int(dice_str)
        except ValueError:
            count, sides = 1, 20

        raw_rolls = [renpy.random.randint(1, sides) for _ in range(count)]
        chosen_roll = None
        
        if pending_dice_roll.dice_type == "d20" and (pending_dice_roll.advantage or pending_dice_roll.disadvantage):
            if len(raw_rolls) < 2:
                raw_rolls.append(renpy.random.randint(1, sides))
            chosen_roll = max(raw_rolls) if pending_dice_roll.advantage else min(raw_rolls)
            base_result = chosen_roll
        else:
            base_result = sum(raw_rolls)
            if pending_dice_roll.dice_type == "d20":
                chosen_roll = base_result

        final_result = base_result + pending_dice_roll.modifier
        roll_result = DiceRollResult(pending_dice_roll, raw_rolls, final_result, chosen_roll)
        
        roll_history.append(roll_result)
        if len(roll_history) > 5: roll_history.pop(0)
        
        last_roll_result = roll_result
        pending_dice_roll = None
        
        # --- MODIFIED LOGIC ---
        # This section now passes only the raw dice results to the combat engine.
        combat_manager = get_combat_manager()
        if combat_manager:
            if combat_manager.combat_state == 'awaiting_player_roll':
                if chosen_roll is not None:
                    ui_process_player_d20_roll(chosen_roll) # Pass only the raw d20
            
            elif combat_manager.combat_state == 'awaiting_damage_roll':
                ui_process_player_damage_roll(base_result) # Pass the sum of damage dice

        renpy.timeout(0.5)
        dice_animation_playing = False
        return roll_result
    
    def get_roll_color(result, context="general"):
        if context == "attack":
            if result >= 20: return "#FFD700"
            elif result >= 15: return "#00FF00"
            elif result >= 10: return "#FFFF00"
            else: return "#FF6666"
        elif context == "damage": return "#FF4444"
        elif context == "save":
            if result >= 15: return "#00FF00"
            elif result >= 10: return "#FFFF00"
            else: return "#FF6666"
        else: return "#FFFFFF"

screen enhanced_dice_interface(dice_animation_playing, last_roll_result, dice_advantage_state, roll_history):
    modal False
    frame:
        style "dice_main_frame"
        xsize 420
        ysize 600
        xalign 0.0
        yalign 0.0
        vbox:
            spacing 15
            text "DICE ROLL" style "dice_header_text" xalign 0.5
            frame:
                style "dice_target_frame"
                xsize 380
                ysize 120
                $ current_target = None
                $ target_info = None
                $ combat_manager = get_combat_manager()
                if combat_manager and combat_manager.pending_action:
                    $ current_target = combat_manager.pending_action.get("target")
                    if current_target:
                        $ target_info = { "name": current_target.get_name(), "hp": current_target.current_hp, "max_hp": current_target.character_data.max_hp, "ac": current_target.get_ac() }

                hbox:
                    spacing 10
                    xalign 0.5
                    yalign 0.5
                    if target_info:
                        vbox:
                            spacing 5
                            text "[target_info['name']]" color "#FFFFFF" size 18 bold True
                            text "HP: [target_info['hp']]/[target_info['max_hp']]" color "#FF6666" size 16
                            text "AC: [target_info['ac']]" color "#6666FF" size 16
                    else:
                        vbox:
                            spacing 5
                            xalign 0.5
                            yalign 0.5
                            text "No Target" color "#CCCCCC" size 16 xalign 0.5
                            text "Select an action" color "#888888" size 14 xalign 0.5
            frame:
                style "dice_display_frame"
                xsize 380
                ysize 200
                if dice_animation_playing:
                    frame:
                        background "#FF6666"
                        xalign 0.5
                        yalign 0.5
                        xsize 100
                        ysize 100
                        text "?" size 60 color "#FFFFFF" xalign 0.5 yalign 0.5
                        at transform:
                            rotate 0
                            linear 0.1 rotate 90
                            linear 0.1 rotate 180
                            linear 0.1 rotate 270
                            linear 0.1 rotate 360
                            repeat
                elif last_roll_result:
                    vbox:
                        spacing 10
                        xalign 0.5
                        yalign 0.5
                        $ result_color = get_roll_color(last_roll_result.final_result, last_roll_result.request.context)
                        text "[last_roll_result.final_result]" size 80 color result_color xalign 0.5 bold True
                        text "[last_roll_result.format_display()]" size 20 color "#CCCCCC" xalign 0.5
                else:
                    text "Ready to roll..." size 30 color "#888888" xalign 0.5 yalign 0.5
            frame:
                style "dice_control_frame"
                xsize 380
                ysize 60
                hbox:
                    spacing 10
                    xfill True
                    textbutton "Normal":
                        style "dice_adv_button"
                        text_style "dice_button_text"
                        action SetVariable("dice_advantage_state", "normal")
                        background If(dice_advantage_state == "normal", "#4A4A4A", "#2A2A2A")
                    textbutton "Advantage":
                        style "dice_adv_button"
                        text_style "dice_button_text"
                        action SetVariable("dice_advantage_state", "advantage")
                        background If(dice_advantage_state == "advantage", "#228B22", "#2A2A2A")
                    textbutton "Disadvantage":
                        style "dice_adv_button"
                        text_style "dice_button_text"
                        action SetVariable("dice_advantage_state", "disadvantage")
                        background If(dice_advantage_state == "disadvantage", "#DC143C", "#2A2A2A")
            frame:
                style "dice_control_frame"
                xsize 380
                ysize 120
                vbox:
                    spacing 8
                    text "Quick Rolls:" style "dice_label_text"
                    grid 2 2:
                        spacing 10
                        xfill True
                        $ can_roll_attack = get_combat_manager() and get_combat_manager().combat_state == 'awaiting_player_roll'
                        $ can_roll_damage = get_combat_manager() and get_combat_manager().combat_state == 'awaiting_damage_roll'
                        textbutton "Attack Roll" style "dice_quick_button" text_style "dice_button_text" action Function(quick_attack_roll) sensitive can_roll_attack
                        textbutton "Damage Roll" style "dice_quick_button" text_style "dice_button_text" action Function(quick_damage_roll) sensitive can_roll_damage
                        textbutton "Saving Throw" style "dice_quick_button" text_style "dice_button_text" action Function(quick_save_roll) sensitive not (can_roll_attack or can_roll_damage)
                        textbutton "Skill Check" style "dice_quick_button" text_style "dice_button_text" action Function(quick_skill_roll) sensitive not (can_roll_attack or can_roll_damage)
            frame:
                style "dice_control_frame"
                xsize 380
                ysize 80
                vbox:
                    spacing 8
                    text "Custom Roll:" style "dice_label_text"
                    hbox:
                        spacing 10
                        textbutton "d4" style "dice_type_button" text_style "dice_small_button_text" action Function(custom_roll, "d4")
                        textbutton "d6" style "dice_type_button" text_style "dice_small_button_text" action Function(custom_roll, "d6")
                        textbutton "d8" style "dice_type_button" text_style "dice_small_button_text" action Function(custom_roll, "d8")
                        textbutton "d10" style "dice_type_button" text_style "dice_small_button_text" action Function(custom_roll, "d10")
                        textbutton "d12" style "dice_type_button" text_style "dice_small_button_text" action Function(custom_roll, "d12")
                        textbutton "d20" style "dice_type_button" text_style "dice_small_button_text" action Function(custom_roll, "d20")
            if roll_history:
                frame:
                    style "dice_history_frame"
                    xsize 380
                    ysize 100
                    vbox:
                        spacing 5
                        text "Recent Rolls:" style "dice_label_text"
                        viewport:
                            xsize 360
                            ysize 70
                            scrollbars "vertical"
                            mousewheel True
                            vbox:
                                spacing 3
                                for roll_result in reversed(roll_history[-5:]):
                                    $ history_color = get_roll_color(roll_result.final_result, roll_result.request.context)
                                    text "[roll_result.format_display()]" size 16 color history_color

init python:
    #======================================================================
    # MODIFIED FUNCTION
    #======================================================================
    def quick_attack_roll():
        """
        This function is now simplified. It no longer calculates bonuses.
        It just queues a d20 roll for the combat engine to process.
        """
        advantage = dice_advantage_state == "advantage"
        disadvantage = dice_advantage_state == "disadvantage"
        # Modifier is 0 because the combat engine will calculate all bonuses.
        queue_dice_roll("d20", 0, "attack", advantage, disadvantage, "Attack")
        execute_dice_roll()
    
    #======================================================================
    # MODIFIED FUNCTION
    #======================================================================
    def quick_damage_roll():
        """
        This function is now much simpler. It determines the correct dice to roll
        (including for crits) but does NOT add any bonuses. The combat engine handles that.
        """
        combat_manager = get_combat_manager()
        if not combat_manager or not combat_manager.pending_action:
            queue_dice_roll("1d6", 0, "damage", False, False, "Damage")
            execute_dice_roll()
            return

        weapon = combat_manager.pending_action.get("weapon")
        is_critical = combat_manager.pending_action.get("is_critical", False)
        if not weapon: return

        damage_dice = weapon.effects.get("damage", "1d4")
        if is_critical:
            try:
                num_dice_str, sides_str = damage_dice.split('d')
                num_dice = int(num_dice_str) * 2
                damage_dice = "{}d{}".format(num_dice, sides_str)
            except ValueError:
                pass
        # Modifier is 0 because the combat engine will calculate all bonuses.
        queue_dice_roll(damage_dice, 0, "damage", False, False, "Damage")
        execute_dice_roll()
    
    def quick_save_roll():
        queue_dice_roll("d20", 0, "save", dice_advantage_state == "advantage", dice_advantage_state == "disadvantage", "Save")
        execute_dice_roll()
    
    def quick_skill_roll():
        queue_dice_roll("d20", 0, "skill", dice_advantage_state == "advantage", dice_advantage_state == "disadvantage", "Skill")
        execute_dice_roll()
    
    def custom_roll(dice_type):
        queue_dice_roll(dice_type, 0, "general", False, False, "Custom {}".format(dice_type))
        execute_dice_roll()

# Styles (remain unchanged)
style dice_main_frame:
    background "#1a1a2e"
    padding (20, 20)
style dice_header_text:
    size 32
    color "#FFFFFF"
    bold True
style dice_display_frame:
    background "#16213e"
    padding (15, 15)
style dice_control_frame:
    background "#2a2a3a"
    padding (10, 10)
style dice_history_frame:
    background "#2a2a3a"
    padding (10, 10)
style dice_label_text:
    size 18
    color "#CCCCCC"
    bold True
style dice_button_text:
    size 16
    color "#FFFFFF"
    hover_color "#FFD700"
style dice_small_button_text:
    size 14
    color "#FFFFFF"
    hover_color "#FFD700"
style dice_adv_button:
    padding (8, 4)
    hover_background "#5a5a5a"
style dice_quick_button:
    padding (6, 3)
    background "#3a3a4a"
    hover_background "#5a5a6a"
style dice_type_button:
    padding (4, 2)
    background "#3a3a4a"
    hover_background "#5a5a6a"
    xsize 40
