#============================================================================
# ENHANCED DICE ROLL INTERFACE SYSTEM
#============================================================================
# This file contains the new dice rolling interface with visual enhancements,
# animations, and improved usability for the combat system
#============================================================================

# Dice roll state variables
default pending_dice_roll = None
default dice_animation_playing = False
default last_roll_result = None
default roll_history = []  # Store last 5 rolls
default dice_advantage_state = "normal"  # "normal", "advantage", "disadvantage"
default dice_context = "general"  # "attack", "damage", "save", "skill", "general"

python early:
    import time
    
    class DiceRollRequest:
        """Represents a dice roll request with all necessary parameters"""
        def __init__(self, dice_type="d20", modifier=0, context="general", 
                     advantage=False, disadvantage=False, label="Roll"):
            self.dice_type = dice_type
            self.modifier = modifier
            self.context = context
            self.advantage = advantage
            self.disadvantage = disadvantage
            self.label = label
            self.timestamp = time.time()
    
    class DiceRollResult:
        """Stores the result of a dice roll with display formatting"""
        def __init__(self, roll_request, raw_rolls, final_result, chosen_roll=None):
            self.request = roll_request
            self.raw_rolls = raw_rolls  # List of individual dice results
            self.final_result = final_result  # Final result after modifiers
            self.chosen_roll = chosen_roll  # For advantage/disadvantage
            self.timestamp = time.time()
            
        def format_display(self):
            """Format the result for display"""
            if self.request.advantage or self.request.disadvantage:
                adv_text = "ADV" if self.request.advantage else "DIS"
                return f"{self.request.dice_type}({','.join(map(str, self.raw_rolls))}) [{adv_text}:{self.chosen_roll}] {'+' if self.request.modifier >= 0 else ''}{self.request.modifier} = {self.final_result}"
            else:
                if self.request.modifier != 0:
                    return f"{self.request.dice_type}({self.raw_rolls[0]}) {'+' if self.request.modifier >= 0 else ''}{self.request.modifier} = {self.final_result}"
                else:
                    return f"{self.request.dice_type}({self.raw_rolls[0]}) = {self.final_result}"

# Dice roll processing functions
init python:
    def queue_dice_roll(dice_type="d20", modifier=0, context="general", advantage=False, disadvantage=False, label="Roll"):
        """Queue a new dice roll request"""
        global pending_dice_roll
        pending_dice_roll = DiceRollRequest(dice_type, modifier, context, advantage, disadvantage, label)
        
    def execute_dice_roll():
        """Execute the pending dice roll and store result"""
        global pending_dice_roll, last_roll_result, roll_history, dice_animation_playing
        
        if not pending_dice_roll:
            return None
            
        # Start animation
        dice_animation_playing = True
        
        # Parse dice type (e.g., "d20", "2d6")
        dice_str = pending_dice_roll.dice_type
        if dice_str.startswith('d'):
            count = 1
            sides = int(dice_str[1:])
        else:
            parts = dice_str.split('d')
            count = int(parts[0])
            sides = int(parts[1])
        
        # Roll the dice
        raw_rolls = []
        for _ in range(count):
            raw_rolls.append(renpy.random.randint(1, sides))
        
        # Handle advantage/disadvantage for d20 rolls
        chosen_roll = None
        if pending_dice_roll.dice_type == "d20" and (pending_dice_roll.advantage or pending_dice_roll.disadvantage):
            # Roll a second d20
            second_roll = renpy.random.randint(1, sides)
            raw_rolls.append(second_roll)
            
            if pending_dice_roll.advantage:
                chosen_roll = max(raw_rolls)
            else:  # disadvantage
                chosen_roll = min(raw_rolls)
        else:
            chosen_roll = sum(raw_rolls) if count > 1 else raw_rolls[0]
        
        # Calculate final result
        base_result = chosen_roll if chosen_roll is not None else sum(raw_rolls)
        final_result = base_result + pending_dice_roll.modifier
        
        # Create result object
        roll_result = DiceRollResult(pending_dice_roll, raw_rolls, final_result, chosen_roll)
        
        # Store in history (keep last 5)
        roll_history.append(roll_result)
        if len(roll_history) > 5:
            roll_history.pop(0)
        
        # Set as last result and clear pending
        last_roll_result = roll_result
        pending_dice_roll = None
        
        # Process the roll result in combat if we're in combat
        if hasattr(store, 'enhanced_combat_controller') and hasattr(store, 'process_dice_roll_result'):
            try:
                store.process_dice_roll_result(roll_result)
            except:
                pass  # Silently handle if not in combat context
        
        # Animation will be stopped by the screen update
        renpy.timeout(0.5)  # Brief delay for animation effect
        dice_animation_playing = False
        
        return roll_result
    
    def get_roll_color(result, context="general"):
        """Get color for roll result based on context and value"""
        if context == "attack":
            if result >= 20:
                return "#FFD700"  # Gold for natural 20
            elif result >= 15:
                return "#00FF00"  # Green for good hits
            elif result >= 10:
                return "#FFFF00"  # Yellow for marginal hits
            else:
                return "#FF6666"  # Red for likely misses
        elif context == "damage":
            return "#FF4444"  # Red for damage
        elif context == "save":
            if result >= 15:
                return "#00FF00"  # Green for good saves
            elif result >= 10:
                return "#FFFF00"  # Yellow for marginal
            else:
                return "#FF6666"  # Red for fails
        else:
            return "#FFFFFF"  # Default white

# Enhanced dice roll screen
screen enhanced_dice_interface():
    modal False
    
    frame:
        style "dice_main_frame"
        xsize 420
        ysize 600
        xalign 0.0
        yalign 0.0
        
        vbox:
            spacing 15
            
            # Header
            text "DICE ROLL" style "dice_header_text" xalign 0.5
            
            # Target Character Image Display
            frame:
                style "dice_target_frame"
                xsize 380
                ysize 120
                
                # Determine current target/enemy for image display
                $ current_target = None
                $ target_image = None
                $ target_info = None
                
                if combat_participants and current_turn_index < len(combat_participants):
                    $ current_participant = combat_participants[current_turn_index]
                    
                    # Show the current active participant (enemy) or selected target
                    if pending_roll and pending_roll.get("target"):
                        $ current_target = pending_roll["target"]
                    elif selected_target:
                        $ current_target = selected_target
                    elif current_participant != player_stats:
                        $ current_target = current_participant
                    elif len(combat_participants) > 1:
                        # Show first non-player participant
                        for participant in combat_participants:
                            if participant != player_stats:
                                $ current_target = participant
                                break
                
                if current_target:
                    $ target_info = get_character_combat_info(current_target)
                    # Get character image using proper function
                    $ character_name = getattr(current_target, 'name', '')
                    $ target_image = get_character_image(character_name, "idle", True)
                    
                    # Fallback to default if no image found
                    if not target_image:
                        $ target_image = "images/default_combat_img.png"
                
                hbox:
                    spacing 10
                    xalign 0.5
                    yalign 0.5
                    
                    if target_image:
                        # Display scaled character/enemy image
                        add target_image:
                            xsize 80
                            ysize 80
                            xalign 0.0
                        
                        # Character info
                        if target_info:
                            vbox:
                                spacing 5
                                text "[target_info['name']]" color "#FFFFFF" size 18 bold True
                                text "HP: [target_info['hp']]/[target_info['max_hp']]" color "#FF6666" size 16
                                text "AC: [target_info['ac']]" color "#6666FF" size 16
                    else:
                        # Fallback display when no target/image available
                        vbox:
                            spacing 5
                            xalign 0.5
                            yalign 0.5
                            
                            text "No Target" color "#CCCCCC" size 16 xalign 0.5
                            text "Select an action" color "#888888" size 14 xalign 0.5
            
            # Main dice display area
            frame:
                style "dice_display_frame"
                xsize 380
                ysize 200
                
                if dice_animation_playing:
                    # Animated dice (placeholder for now)
                    frame:
                        background "#FF6666"
                        xalign 0.5
                        yalign 0.5
                        xsize 100
                        ysize 100
                        
                        text "?" size 60 color "#FFFFFF" xalign 0.5 yalign 0.5
                        
                        # Add rotation animation
                        at transform:
                            rotate 0
                            linear 0.1 rotate 90
                            linear 0.1 rotate 180
                            linear 0.1 rotate 270
                            linear 0.1 rotate 360
                            repeat
                
                elif last_roll_result:
                    # Display last roll result
                    vbox:
                        spacing 10
                        xalign 0.5
                        yalign 0.5
                        
                        # Large result number
                        $ result_color = get_roll_color(last_roll_result.final_result, last_roll_result.request.context)
                        text "[last_roll_result.final_result]" size 80 color result_color xalign 0.5 bold True
                        
                        # Breakdown
                        text "[last_roll_result.format_display()]" size 20 color "#CCCCCC" xalign 0.5
                        
                else:
                    # No roll yet
                    text "Ready to roll..." size 30 color "#888888" xalign 0.5 yalign 0.5
            
            # Advantage/Disadvantage selector
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
                        if dice_advantage_state == "normal":
                            background "#4A4A4A"
                        else:
                            background "#2A2A2A"
                    
                    textbutton "Advantage":
                        style "dice_adv_button"
                        text_style "dice_button_text"
                        action SetVariable("dice_advantage_state", "advantage")
                        if dice_advantage_state == "advantage":
                            background "#228B22"
                        else:
                            background "#2A2A2A"
                    
                    textbutton "Disadvantage":
                        style "dice_adv_button"
                        text_style "dice_button_text"
                        action SetVariable("dice_advantage_state", "disadvantage")
                        if dice_advantage_state == "disadvantage":
                            background "#DC143C"
                        else:
                            background "#2A2A2A"
            
            # Quick roll buttons
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
                        
                        textbutton "Attack Roll":
                            style "dice_quick_button"
                            text_style "dice_button_text"
                            action Function(quick_attack_roll)
                        
                        textbutton "Damage Roll":
                            style "dice_quick_button"
                            text_style "dice_button_text"
                            action Function(quick_damage_roll)
                        
                        textbutton "Saving Throw":
                            style "dice_quick_button"
                            text_style "dice_button_text"
                            action Function(quick_save_roll)
                        
                        textbutton "Skill Check":
                            style "dice_quick_button"
                            text_style "dice_button_text"
                            action Function(quick_skill_roll)
            
            # Custom roll input
            frame:
                style "dice_control_frame"
                xsize 380
                ysize 80
                
                vbox:
                    spacing 8
                    
                    text "Custom Roll:" style "dice_label_text"
                    
                    hbox:
                        spacing 10
                        
                        # Dice type buttons
                        textbutton "d4":
                            style "dice_type_button"
                            text_style "dice_small_button_text"
                            action Function(custom_roll, "d4")
                        
                        textbutton "d6":
                            style "dice_type_button"
                            text_style "dice_small_button_text"
                            action Function(custom_roll, "d6")
                        
                        textbutton "d8":
                            style "dice_type_button"
                            text_style "dice_small_button_text"
                            action Function(custom_roll, "d8")
                        
                        textbutton "d10":
                            style "dice_type_button"
                            text_style "dice_small_button_text"
                            action Function(custom_roll, "d10")
                        
                        textbutton "d12":
                            style "dice_type_button"
                            text_style "dice_small_button_text"
                            action Function(custom_roll, "d12")
                        
                        textbutton "d20":
                            style "dice_type_button"
                            text_style "dice_small_button_text"
                            action Function(custom_roll, "d20")
            
            # Roll history
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

# Quick roll functions
init python:
    def quick_attack_roll():
        """Execute a quick attack roll with current character's modifiers"""
        # Get current participant's attack bonus
        current_participant = enhanced_combat_controller.get_current_participant()
        if current_participant:
            str_mod = (getattr(current_participant, 'strength', 10) - 10) // 2
            prof_bonus = getattr(current_participant, 'proficiency_bonus', 2)
            atk_bonus = getattr(current_participant, 'atk_bonus', 0)
            total_bonus = str_mod + prof_bonus + atk_bonus
        else:
            total_bonus = 0
        
        advantage = dice_advantage_state == "advantage"
        disadvantage = dice_advantage_state == "disadvantage"
        
        queue_dice_roll("d20", total_bonus, "attack", advantage, disadvantage, "Attack")
        execute_dice_roll()
    
    def quick_damage_roll():
        """Execute a quick damage roll"""
        # Default damage roll - could be enhanced to use current weapon
        queue_dice_roll("d6", 0, "damage", False, False, "Damage")
        execute_dice_roll()
    
    def quick_save_roll():
        """Execute a quick saving throw"""
        queue_dice_roll("d20", 0, "save", dice_advantage_state == "advantage", dice_advantage_state == "disadvantage", "Save")
        execute_dice_roll()
    
    def quick_skill_roll():
        """Execute a quick skill check"""
        queue_dice_roll("d20", 0, "skill", dice_advantage_state == "advantage", dice_advantage_state == "disadvantage", "Skill")
        execute_dice_roll()
    
    def custom_roll(dice_type):
        """Execute a custom dice roll"""
        queue_dice_roll(dice_type, 0, "general", dice_advantage_state == "advantage", dice_advantage_state == "disadvantage", f"Custom {dice_type}")
        execute_dice_roll()

# Dice interface styles
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
