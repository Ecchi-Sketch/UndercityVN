# == 0. Character Profiles and Attributes =====================================
# Define default variables for the player's main stat object and background.
default player_stats = None
default player_name = "Player"
default player_background = ""

# Use an init python block to define the character profiles as classes.
# This keeps the data organized and easy to access on the creation screen.
init python:
    class Profile:
        def __init__(self, name, hp, ac, str, dex, con, intl, wis, cha, summary, backstory):
            self.name = name
            self.hp = hp
            self.ac = ac
            # Store attributes as a dictionary for easy display
            self.attributes = {
                "Strength": str,
                "Dexterity": dex,
                "Constitution": con,
                "Intelligence": intl,
                "Wisdom": wis,
                "Charisma": cha
            }
            self.summary = summary
            self.backstory = backstory

    # Create the dictionary of available profiles
    profiles = {
        "Boxer": Profile(
            "The Boxer",
            hp=20, ac=14, str=16, dex=12, con=14, intl=8, wis=10, cha=10,
            summary="A straightforward brawler. You solve problems with your fists and intimidate those who stand in your way. You're tough, direct, and your powerful punches are your most valuable asset.",
            backstory="You made a name for yourself in the fighting pits of a lesser city. Seeking bigger prizes and tougher competition, you came to the City of Progress, but your reputation for violence preceded you, leading to a hasty stowaway journey to escape the law."
        ),
        "Thief": Profile(
            "The Thief",
            hp=16, ac=15, str=10, dex=16, con=10, intl=12, wis=14, cha=8,
            summary="A creature of the shadows. You avoid direct confrontation, preferring to use stealth and cunning to achieve your goals. You excel at finding hidden paths and noticing details others miss.",
            backstory="Orphaned on the streets, you learned early that survival meant being quicker and quieter than everyone else. After a heist went wrong, you stowed away on the first airship out, leaving your past and a very angry guild behind you."
        ),
        "Con-man": Profile(
            "The Con-man",
            hp=16, ac=12, str=8, dex=12, con=10, intl=14, wis=10, cha=16,
            summary="A silver-tongued devil. Your greatest weapon is your wit. You can talk your way into the most secure vaults and out of the tightest spots. Deception and persuasion are the tools of your trade.",
            backstory="You've always lived by your wits, swindling merchants and nobles with elaborate schemes. But a con targeting the wrong person forced you to flee with nothing but the clothes on your back and a ticket for the nearest airship."
        )
    }

    # This variable will hold the profile currently being viewed on the creation screen.
    selected_profile = profiles["Boxer"]


# == 3. Character Creation Screen =============================================
screen character_creation():
    tag menu
    add "bg_char_creation" # Use a background for this screen

    # Use a frame for the main content to give it a border and background
    frame:
        xalign 0.5
        yalign 0.5
        xsize 0.85
        padding (25, 25)

        vbox:
            spacing 10

            label "Create Your Character" style "header"
            text "Define your identity before stepping into the world of Zaun." style "body_text"

            # --- Name Input ---
            hbox:
                spacing 20
                label "Name:"
                input id "player_name" default player_name value VariableInputValue("player_name")

            # --- Profile Selection ---
            hbox:
                spacing 20
                textbutton "The Boxer" action SetVariable("selected_profile", profiles["Boxer"])
                textbutton "The Thief" action SetVariable("selected_profile", profiles["Thief"])
                textbutton "The Con-man" action SetVariable("selected_profile", profiles["Con-man"])

            # --- Profile Details Display ---
            frame:
                style "frame"
                yminimum 250
                vbox:
                    spacing 8
                    text selected_profile.name style "header"
                    hbox:
                        spacing 15
                        # Display the base attributes
                        for key, value in selected_profile.attributes.items():
                            text "{}: {}".format(key, value) style "body_text"
                        # Also display HP and AC
                        text "HP: [selected_profile.hp]" style "body_text"
                        text "AC: [selected_profile.ac]" style "body_text"

                    text "Playstyle: [selected_profile.summary]" style "body_text"
                    text "Backstory: [selected_profile.backstory]" style "body_text"

            # --- Confirmation Button ---
            textbutton "Confirm and Begin" action [
                # This action now creates the player_stats object from the selected profile
                SetVariable("player_stats", CharacterStats(
                    name=player_name,
                    hp=selected_profile.hp,
                    ac=selected_profile.ac,
                    str=selected_profile.attributes["Strength"],
                    dex=selected_profile.attributes["Dexterity"],
                    con=selected_profile.attributes["Constitution"],
                    intl=selected_profile.attributes["Intelligence"],
                    wis=selected_profile.attributes["Wisdom"],
                    cha=selected_profile.attributes["Charisma"]
                )),
                SetVariable("player_background", selected_profile.name),
                Jump("game_start")
            ]
