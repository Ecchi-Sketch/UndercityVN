# == 0. Character Profiles and Attributes =====================================
# Define default variables for the player's name, background, and gender.
# The 'player_stats' object is now defined in NPCRoster.rpy to fix the error.
default player_name = "Player"
default player_background = ""
default selected_gender = "Unspecified"
default selected_pronouns = {"subject": "they", "object": "them", "possessive": "their"}

# Use an init python block to define the character profiles as classes.
init python:
    class Profile:
        def __init__(self, name, hp, ac, str, dex, con, intl, wis, cha, summary, backstory):
            self.name = name
            self.hp = hp
            self.ac = ac
            self.attributes = {
                "Strength": str, "Dexterity": dex, "Constitution": con,
                "Intelligence": intl, "Wisdom": wis, "Charisma": cha
            }
            self.summary = summary
            self.backstory = backstory

    profiles = {
        "Boxer": Profile(
            "The Boxer", hp=200, ac=1, str=16, dex=12, con=140, intl=8, wis=10, cha=10,
            summary="A straightforward brawler. You solve problems with your fists and intimidate those who stand in your way. You're tough, direct, and your powerful punches are your most valuable asset.",
            backstory="You made a name for yourself in the fighting pits of a lesser city. Seeking bigger prizes and tougher competition, you came to the City of Progress, but your reputation for violence preceded you, leading to a hasty stowaway journey to escape the law."
        ),
        "Thief": Profile(
            "The Thief", hp=16, ac=15, str=10, dex=16, con=10, intl=12, wis=14, cha=8,
            summary="A creature of the shadows. You avoid direct confrontation, preferring to use stealth and cunning to achieve your goals. You excel at finding hidden paths and noticing details others miss.",
            backstory="Orphaned on the streets, you learned early that survival meant being quicker and quieter than everyone else. After a heist went wrong, you stowed away on the first airship out, leaving your past and a very angry guild behind you."
        ),
        "Con-man": Profile(
            "The Con-man", hp=16, ac=12, str=8, dex=12, con=10, intl=14, wis=10, cha=16,
            summary="A silver-tongued devil. Your greatest weapon is your wit. You can talk your way into the most secure vaults and out of the tightest spots. Deception and persuasion are the tools of your trade.",
            backstory="You've always lived by your wits, swindling merchants and nobles with elaborate schemes. But a con targeting the wrong person forced you to flee with nothing but the clothes on your back and a ticket for the nearest airship."
        )
    }
    
    # Gender options with corresponding pronouns
    gender_options = {
        "Male": {"subject": "he", "object": "him", "possessive": "his"},
        "Female": {"subject": "she", "object": "her", "possessive": "her"},
        "Non-binary": {"subject": "they", "object": "them", "possessive": "their"},
        "Unspecified": {"subject": "they", "object": "them", "possessive": "their"}
    }
    
    selected_profile = profiles["Boxer"]

    # This function now updates the existing player_stats object instead of creating a new one.
    def finalize_character_creation():
        global player_stats, player_name, player_background, selected_profile, selected_gender, selected_pronouns
        
        # Update the stats of the global player_stats object
        player_stats.name = player_name
        player_stats.base_max_hp = selected_profile.hp
        player_stats.base_ac = selected_profile.ac
        player_stats.strength = selected_profile.attributes["Strength"]
        player_stats.dexterity = selected_profile.attributes["Dexterity"]
        player_stats.constitution = selected_profile.attributes["Constitution"]
        player_stats.intelligence = selected_profile.attributes["Intelligence"]
        player_stats.wisdom = selected_profile.attributes["Wisdom"]
        player_stats.charisma = selected_profile.attributes["Charisma"]
        
        # Set the background
        player_background = selected_profile.name
        
        # Set gender and pronouns
        player_stats.gender = selected_gender
        player_stats.pronouns = selected_pronouns
        
        # Recalculate stats to apply any initial bonuses and set current HP
        player_stats.recalculate_stats()
        player_stats.hp = player_stats.max_hp


# == 3. Character Creation Screen =============================================
screen character_creation():
    tag menu
    add "bg_char_creation"

    frame:
        xalign 0.5
        yalign 0.5
        xsize 0.85
        padding (25, 25)

        vbox:
            spacing 10
            label "Create Your Character" style "header"
            text "Define your identity before stepping into the world of Zaun." style "body_text"

            hbox:
                spacing 20
                label "Name:"
                input id "player_name" default player_name value VariableInputValue("player_name")

            hbox:
                spacing 20
                label "Gender:"
                textbutton "Male" action [SetVariable("selected_gender", "Male"), SetVariable("selected_pronouns", gender_options["Male"])]
                textbutton "Female" action [SetVariable("selected_gender", "Female"), SetVariable("selected_pronouns", gender_options["Female"])]
                textbutton "Non-binary" action [SetVariable("selected_gender", "Non-binary"), SetVariable("selected_pronouns", gender_options["Non-binary"])]
                textbutton "Unspecified" action [SetVariable("selected_gender", "Unspecified"), SetVariable("selected_pronouns", gender_options["Unspecified"])]

            hbox:
                spacing 20
                textbutton "The Boxer" action SetVariable("selected_profile", profiles["Boxer"])
                textbutton "The Thief" action SetVariable("selected_profile", profiles["Thief"])
                textbutton "The Con-man" action SetVariable("selected_profile", profiles["Con-man"])

            frame:
                style "frame"
                yminimum 250
                vbox:
                    spacing 8
                    text selected_profile.name style "header"
                    hbox:
                        spacing 15
                        for key, value in selected_profile.attributes.items():
                            text "{}: {}".format(key, value) style "body_text"
                        text "HP: [selected_profile.hp]" style "body_text"
                        text "AC: [selected_profile.ac]" style "body_text"
                    text "Playstyle: [selected_profile.summary]" style "body_text"
                    text "Backstory: [selected_profile.backstory]" style "body_text"

            textbutton "Confirm and Begin" action [
                # This now calls our helper function and then jumps to the game start.
                Function(finalize_character_creation),
                Jump("game_start")
            ]
