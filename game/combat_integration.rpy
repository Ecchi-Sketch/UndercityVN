# GameScripts/combat_integration.rpy

# --- DICE UI STATE VARIABLES ---
default pending_dice_roll = None
default dice_animation_playing = False
default last_roll_result = None
default roll_history = []
default dice_advantage_state = "normal"
default dice_context = "general"


init python:
    # --- NARRATIVE GENERATOR CLASS ---
    try:
        import spacy
        nlp_model = None
        try:
            nlp_model = spacy.load(renpy.config.basedir + "/game/en_core_web_sm")
            print("spaCy model 'en_core_web_sm' loaded successfully.")
        except Exception as e:
            print("Could not load spaCy model. Narrative generation will be limited. Error: {}".format(e))
    except ImportError as e:
        print("Failed to import spaCy or its dependencies (like NumPy). spaCy features will be disabled. Error: {}".format(e))
        spacy = None
        nlp_model = None

    class NarrativeGenerator:
        def __init__(self):
            self.templates = {
                "hit": ["{actor} lunges forward, striking {target} squarely with their {weapon}!", "A swift attack from {actor} finds its mark, hitting {target}.", "{actor}'s {weapon} connects with a solid thud against {target}."],
                "miss": ["{actor}'s attack goes wide, missing {target} completely.", "{target} deftly sidesteps the blow from {actor}'s {weapon}.", "The attack from {actor} is clumsy, posing no threat to {target}."],
                "critical_hit": ["A brutal, perfectly-placed strike! {actor}'s {weapon} smashes into {target} with devastating force!", "Incredible! {actor} lands a critical blow on {target}, leaving them reeling!", "A flash of steel! {actor} exploits an opening, delivering a massive hit to {target} with their {weapon}."],
                "critical_fumble": ["A disastrous fumble! {actor}'s {weapon} slips, the attack failing spectacularly.", "In a moment of sheer incompetence, {actor} stumbles, completely botching the attack on {target}.", "{actor}'s attack is so wild it throws them off balance, a critical failure."],
                "target_defeated": ["The blow is too much! {target} collapses to the ground, defeated!", "With a final gasp, {target} falls, unable to continue the fight."],
                "finishing_blow_lethal": ["{actor} delivers a final, merciless blow, ending {target}'s struggle permanently.", "With cold efficiency, {actor} finishes the job. {target} will not be getting back up."],
                "finishing_blow_nonlethal": ["{actor} pulls the blow at the last second, knocking {target} unconscious but sparing their life.", "Choosing mercy, {actor} ensures {target} is merely incapacitated, not killed."]
            }
        def generate_prose(self, event):
            event_type = event.get("event_type")
            if event_type == "attack_resolution":
                key = "miss"
                if event.get("hit"): key = "hit"
                if event.get("is_critical_hit"): key = "critical_hit"
                if event.get("is_critical_fumble"): key = "critical_fumble"
                template = renpy.random.choice(self.templates.get(key, []))
                if not template: return "An action occurs."
                return template.format(actor=event.get("actor_name", "Someone"), target=event.get("target_name", "Someone"), weapon=event.get("weapon_name", "their hands"))
            elif event_type == "damage_resolution":
                prose = "The hit deals {} damage!".format(event.get("total_damage", 0))
                if event.get("target_is_defeated"):
                    defeat_template = renpy.random.choice(self.templates.get("target_defeated", []))
                    if defeat_template: prose += " " + defeat_template.format(target=event.get("target_name", "Someone"))
                return prose
            return None
        def generate_finishing_blow_prose(self, actor_name, target_name, choice):
            key = "finishing_blow_lethal" if choice == "lethal" else "finishing_blow_nonlethal"
            template = renpy.random.choice(self.templates.get(key, []))
            if not template: return ""
            return template.format(actor=actor_name, target=target_name)

    # --- COMBAT INTEGRATION LOGIC ---
    combat_manager_ref = [None]
    narrative_gen = NarrativeGenerator()

    def get_combat_manager():
        return combat_manager_ref[0]

    def format_mechanical_log_entry(log_entry):
        event_type = log_entry.get("event_type")
        if event_type == "combat_start": return "Combat has begun! Initiative order: {}".format(", ".join(log_entry.get("turn_order", [])))
        elif event_type == "round_start": return "=== Round {} ===".format(log_entry.get("round_number", 0))
        elif event_type == "attack_resolution":
            actor, target = log_entry.get("actor_name", "N/A"), log_entry.get("target_name", "N/A")
            total_roll, target_ac = log_entry.get("total_attack_roll", 0), log_entry.get("target_ac", 0)
            if log_entry.get("is_critical_fumble"): return "CRIT FAIL: {} vs {} (Rolled 1)".format(actor, target)
            if log_entry.get("hit"):
                if log_entry.get("is_critical_hit"): return "CRIT HIT: {} vs {}! (Roll: {} vs AC {})".format(actor, target, total_roll, target_ac)
                return "HIT: {} vs {}! (Roll: {} vs AC {})".format(actor, target, total_roll, target_ac)
            return "MISS: {} vs {} (Roll: {} vs AC {})".format(actor, target, total_roll, target_ac)
        elif event_type == "prompt": return log_entry.get("message", "Awaiting player action...")
        elif event_type == "prompt_damage": return "[Player Action Required] {}".format(log_entry.get("message"))
        elif event_type == "damage_resolution": return "DAMAGE: {} deals {} damage to {}. ({} HP left)".format(log_entry.get("actor_name"), log_entry.get("total_damage"), log_entry.get("target_name"), log_entry.get("target_hp_remaining"))
        elif event_type == "prompt_finishing_blow": return "[Player Action Required] {} is defeated. Deliver a finishing blow?".format(log_entry.get("target_name"))
        elif event_type == "finishing_blow_resolution": return "{} performed a {} finishing blow on {}.".format(log_entry.get("actor_name"), log_entry.get("choice"), log_entry.get("target_name"))
        elif event_type == "combat_end": return "[Combat End: {} - {}]".format(log_entry.get("outcome"), log_entry.get("rewards"))
        else: return str(log_entry)

label start_combat(opponents):
    python:
        last_roll_result = None
        roll_history = []
        dice_advantage_state = "normal"
        # MODIFIED: Uses the 'player_stats' object to ensure consistency with the character sheet.
        participants = [player_stats] + opponents
        combat_manager = CombatController(narrative_gen)
        combat_manager.initialize_combat(participants)
        combat_manager_ref[0] = combat_manager
    call screen combat_encounter
    python:
        combat_manager_ref[0] = None
    return
