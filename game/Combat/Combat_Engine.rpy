# This script contains the core logic for the TTRPG combat system.

python early:
    import renpy.store as store
    import random

    # The DiceRoller class handles all dice calculations.
    class DiceRoller:
        def roll(self, dice_string):
            # Parses a dice string like "2d6+3" and returns the result.
            parts = dice_string.replace(' ', '').split('d')
            num_dice = int(parts[0])
            if '+' in parts[1]:
                sides, bonus = map(int, parts[1].split('+'))
            elif '-' in parts[1]:
                sides, bonus = map(int, parts[1].split('-'))
                bonus = -bonus
            else:
                sides = int(parts[1])
                bonus = 0

            total = sum(random.randint(1, sides) for _ in range(num_dice)) + bonus
            return total

    # The CombatManager class orchestrates the entire combat encounter.
    class CombatManager:
        def __init__(self, player, enemies):
            self.player = player
            self.enemies = enemies
            self.combatants = [player] + enemies
            self.turn_order = []
            self.current_turn_index = 0
            self.dice_roller = DiceRoller()

        def start_combat(self):
            # Roll for initiative to determine turn order.
            self.turn_order = sorted(self.combatants, key=lambda x: self.dice_roller.roll("1d20") + x.get_modifier('dexterity'), reverse=True)
            renpy.jump("combat_loop")

        def get_current_combatant(self):
            return self.turn_order[self.current_turn_index]

        def next_turn(self):
            # Advance to the next combatant in the turn order.
            self.current_turn_index = (self.current_turn_index + 1) % len(self.turn_order)
            # Remove any defeated enemies from the turn order.
            self.turn_order = [c for c in self.turn_order if c.hp > 0]
            if not self.is_combat_over():
                renpy.jump("combat_loop")
            else:
                self.end_combat()

        def is_combat_over(self):
            player_alive = any(c == self.player and c.hp > 0 for c in self.turn_order)
            enemies_alive = any(c != self.player and c.hp > 0 for c in self.turn_order)
            return not player_alive or not enemies_alive

        def end_combat(self):
            player_alive = any(c == self.player and c.hp > 0 for c in self.turn_order)
            if player_alive:
                renpy.jump("combat_victory")
            else:
                renpy.jump("combat_defeat")

        def player_attack(self, target_id):
            player = self.player
            target = next((e for e in self.enemies if id(e) == target_id), None)
            if not target:
                return

            # --- Player Attack Roll ---
            attack_roll = self.dice_roller.roll("1d20")
            attack_modifier = player.get_modifier('strength') # Assuming melee
            total_attack = attack_roll + attack_modifier

            renpy.say(None, "You attack the [target.name]! You rolled a [attack_roll] + [attack_modifier] = [total_attack].")

            if total_attack >= target.ac:
                # --- Player Damage Roll ---
                damage_roll = self.dice_roller.roll("1d6") # Example for a basic punch
                damage_modifier = player.get_modifier('strength')
                total_damage = damage_roll + damage_modifier
                target.hp -= total_damage
                renpy.say(None, "It's a hit! You deal [total_damage] damage. The [target.name] has [target.hp] HP remaining.")
            else:
                renpy.say(None, "Your attack misses!")

            self.next_turn()

        def enemy_attack(self, enemy, target):
            # --- Enemy Attack Roll ---
            attack_roll = self.dice_roller.roll("1d20")
            attack_modifier = enemy.get_modifier('strength')
            total_attack = attack_roll + attack_modifier

            renpy.say(None, "The [enemy.name] attacks you! It rolled a [attack_roll] + [attack_modifier] = [total_attack].")

            if total_attack >= target.ac:
                # --- Enemy Damage Roll ---
                damage_roll = self.dice_roller.roll("1d4") # Example for a basic enemy attack
                damage_modifier = enemy.get_modifier('strength')
                total_damage = damage_roll + damage_modifier
                target.hp -= total_damage
                renpy.say(None, "It's a hit! You take [total_damage] damage. You have [target.hp] HP remaining.")
            else:
                renpy.say(None, "The attack misses!")

            self.next_turn()

# Create a global instance of the CombatManager. It will be populated when combat starts.
default combat_manager = None

# --- Combat Screen ---
screen combat_hud():
    # Display the player and enemy stats.
    hbox:
        xalign 0.5
        yalign 0.1
        spacing 50
        vbox:
            label "Player: [player_stats.name]"
            bar value player_stats.hp range player_stats.max_hp
            text "[player_stats.hp] / [player_stats.max_hp] HP"
        for enemy in combat_manager.enemies:
            if enemy.hp > 0:
                vbox:
                    label "[enemy.name]"
                    bar value enemy.hp range enemy.max_hp
                    text "[enemy.hp] / [enemy.max_hp] HP"

# --- Combat Labels ---
label start_combat(enemies):
    # Create a new CombatManager instance with the player and the provided enemies.
    $ global combat_manager
    $ combat_manager = CombatManager(player_stats, enemies)
    call combat_manager.start_combat from _start_combat_call

label combat_loop():
    $ current_char = combat_manager.get_current_combatant()
    if current_char == player_stats:
        # It's the player's turn.
        "It's your turn. What will you do?"
        menu:
            "Attack":
                # Create a sub-menu to choose the target.
                menu:
                    for enemy in combat_manager.enemies:
                        if enemy.hp > 0:
                            "[enemy.name]":
                                call combat_manager.player_attack(id(enemy)) from _player_attack_call
            "Flee":
                "You attempt to flee the battle."
                # Add flee logic here based on your ruleset.
                $ combat_manager.end_combat() # Placeholder
    else:
        # It's an enemy's turn.
        "It's the [current_char.name]'s turn."
        call combat_manager.enemy_attack(current_char, player_stats) from _enemy_attack_call
    return

label combat_victory():
    "You are victorious!"
    # Add XP and loot rewards here based on your ruleset.
    return

label combat_defeat():
    "You have been defeated."
    # Add defeat consequences here based on your ruleset.
    return

# --- Example Usage ---
label example_combat_test:
    # Create a unique instance of a thug for this fight.
    $ thug1 = npc_roster["zaunite_thug_template"].copy()
    "You are suddenly attacked by a Zaunite Thug!"
    call start_combat([thug1])
    "The battle is over."
    return
