#============================================================================
# LLM-ENHANCED COMBAT NARRATIVE GENERATION SYSTEM
#============================================================================
# This file contains the narrative generation system. It now prioritizes
# fetching narration from a local LLM (like LM Studio) for dynamic, cinematic
# descriptions. If the LLM is unavailable, it seamlessly falls back to the
# original, expanded template-based prose system.
#============================================================================

python early:
    import random
    # Import the new function to communicate with the LLM server
    try:
        from llm_integration import get_llm_narration
    except ImportError:
        # Define a dummy function if llm_integration.rpy doesn't exist
        # This prevents the game from crashing if the file is missing.
        def get_llm_narration(prompt):
            return None

    class CombatNarrativeGenerator:
        """Generates rich, well-worded, and expansive prose for combat actions."""
        
        def __init__(self):
            self.spacy_nlp = None
            
            #==================================================================
            # I. ATTACK INITIATION NARRATIVES (FALLBACK)
            # Each entry is a longer, more descriptive scene-setter.
            #==================================================================
            self.weapon_attacks = {
                "sword": [
                    "{attacker_name} closes the distance with a sudden, explosive step. The polished steel of their blade catches the dim light, tracing a deadly arc through the air as it descends towards {target_name}.",
                    "With a calm and steady hand, {attacker_name} raises their sword, the point unwavering as it fixes on {target_name}. They lunge forward, not with a wild charge, but with the focused, lethal precision of a practiced duelist.",
                    "A quick feint to the left draws a reaction from {target_name}. It's the opening {attacker_name} was waiting for, and they pivot hard, bringing their blade around in a powerful, horizontal slash aimed at the midsection."
                ],
                "dagger": [
                    "{attacker_name} melts into the shadows for a split second, reappearing in a blur at {target_name}'s flank. The dagger is held in a reverse grip, poised for a vicious, upward thrust before their opponent can fully register the new position.",
                    "There is no grand motion, only quiet, deadly efficiency. {attacker_name} darts forward, the small blade a near-invisible threat, weaving past {target_name}'s defenses to strike at the gaps in their armor.",
                    "Like a striking viper, {attacker_name}'s arm lashes out. The dagger seems to leap forward, not aimed at causing a massive wound, but at striking a vital nerve cluster to incapacitate {target_name}."
                ],
                "axe": [
                    "A guttural roar tears from {attacker_name}'s throat as they heave the massive axe into the air. The weapon seems to hang there for an eternity before descending with the unstoppable momentum of a falling tree, aimed to cleave {target_name} in two.",
                    "{attacker_name} plants their feet, becoming an anchor of fury. They swing the heavy axe in a wide, horizontal arc, the sheer force of the blow creating a menacing whistle as it cuts through the air.",
                    "Forgoing all defense, {attacker_name} charges forward, leading with the brutal head of the axe. The intent is clear: to shatter, to break, and to utterly overwhelm the defenses of {target_name}."
                ],
                "mace": [
                    "The mace feels heavy and absolute in {attacker_name}'s grip. They advance on {target_name} with measured, deliberate steps, each footfall a drumbeat promising a brutal, bone-shattering conclusion.",
                    "With a grunt of pure exertion, {attacker_name} swings the mace not at {target_name}, but at the ground beside them. The impact sends a shower of dirt and stone into the air, a crude distraction before the real, upward swing begins.",
                    "There is no artistry here, only raw, concussive force. {attacker_name} brings the mace crashing down again and again, hammering at {target_name}'s guard with the relentless rhythm of a forge hammer."
                ],
                "staff": [
                    "The long staff becomes a whirlwind in {attacker_name}'s hands, a dizzying blur of motion that confounds the eye. From the chaos of the spin, one end suddenly shoots forward, a spear-like thrust aimed at {target_name}'s chest.",
                    "Using the staff's length for leverage, {attacker_name} makes a low, sweeping attack. The goal isn't to injure, but to shatter {target_name}'s balance and send them tumbling to the unforgiving ground.",
                    "{attacker_name} uses the staff defensively at first, deflecting a blow from {target_name}. In the same fluid motion, they pivot and bring the other end of the staff around to crack against their opponent's temple."
                ],
                "unarmed": [
                    "With a sharp exhalation, {attacker_name} settles into a low, balanced stance. Their hands, open and ready, become the focal point of their intent as they advance on {target_name}, a picture of disciplined lethality.",
                    "No weapons are needed for this grim work. {attacker_name} explodes into motion, closing the distance with a speed that surprises {target_name}, their fists already coiled for a rapid series of debilitating strikes.",
                    "A powerful front kick from {attacker_name} is aimed to create distance and knock the wind from {target_name}. It's a setup, a brutal opening move in a very personal, physical contest."
                ],
                "knuckles": [
                    "{attacker_name} slowly clenches their fists, the sound of worn leather and scraping iron a low growl of a promise. They raise their guard, the weighted knuckles glinting as they begin to circle {target_name}.",
                    "The fight descends into a desperate, close-quarters brawl. {attacker_name} ducks under a wild swing and drives a brutal, iron-clad hook into the ribs of {target_name}, the impact echoing with a sickening thud.",
                    "It's a flurry of savage blows, each punch from {attacker_name} thrown with the full weight of their body. The iron knuckles are meant to tenderize and break, turning a simple fistfight into something far more grievous."
                ],
                "prosthetic_arm": [
                    "A low hiss of pressurized air escapes the joints of the prosthetic arm. With a surge of shimmer-fueled power, {attacker_name} lunges, their augmented limb a battering ram of steel and fury aimed squarely at {target_name}.",
                    "The prosthetic arm whirs, its metal plates shifting and locking into a combat configuration. {attacker_name} doesn't swing; they piston their arm forward, a straight, concussive blast of force meant to shatter whatever it hits.",
                    "Greenish chem-light begins to pulse from the seams of the augmented limb. {attacker_name} uses the arm to parry a blow from {target_name}, the clang of metal on metal ringing out before they unleash their own counter-attack."
                ],
                "default": [
                    "{attacker_name} fixes their gaze on {target_name}, their expression a mask of cold concentration. They move forward, weapon held at the ready, a predator closing in on their prey.",
                    "The air crackles with tension as {attacker_name} begins their assault. Their movements are economical and practiced, each step and swing a testament to countless hours of training or fighting for their life.",
                    "A sudden, aggressive charge from {attacker_name} is meant to overwhelm {target_name} through sheer audacity. They throw themselves into the attack, betting everything on this single, decisive action."
                ]
            }

            #==================================================================
            # II. ATTACK RESOLUTION NARRATIVES (FALLBACK)
            #==================================================================
            self.hit_results = {
                "critical": [
                    "It's a masterful, brutal strike! The blow lands with a sickening crack, bypassing the defenses of {target_name} with contemptuous ease.",
                    "A flash of brilliance in the chaos of battle! The attack finds a perfect, unguarded opening, striking {target_name} with devastating force.",
                    "An incredible display of power and precision! The attack connects exactly where {attacker_name} intended, the impact staggering their opponent."
                ],
                "hit": [
                    "A solid connection. The weapon finds its home, striking {target_name} with a heavy, jarring thud.",
                    "The blow lands true. It gets past the guard of {target_name}, who grunts in pain from the force of the strike.",
                    "A clean hit. There's no flourish, just the simple, brutal fact of the weapon striking flesh and bone."
                ]
            }
            
            self.miss_results = {
                "dodge": [
                    "But {target_name} is already in motion, a blur of instinct and training. They weave under the blow with inches to spare, the attack finding nothing but empty, stagnant air.",
                    "With a sudden, explosive movement, {target_name} twists away at the last possible second. The attack that should have landed solidly instead slices harmlessly through the space they occupied a moment before.",
                    "The attack is swift, but the reaction from {target_name} is swifter. They give ground, stepping back just beyond the weapon's reach, their eyes never leaving {attacker_name}."
                ],
                "parry": [
                    "A shower of brilliant sparks erupts as steel meets steel. With a sharp ringing sound, {target_name} masterfully parries the blow, their own weapon a firm wall against the assault.",
                    "The attack is turned aside with practiced ease. {target_name} meets the incoming blow, redirecting its force and leaving {attacker_name} momentarily off-balance.",
                    "Reacting with incredible speed, {target_name} gets their weapon up just in time. The resulting clang is a sharp, percussive note in the song of battle, the attack fully negated."
                ],
                "block": [
                    "With a grimace of determination, {target_name} braces for impact. They absorb the full force of the blow on their guard, their arms rattling from the shock but holding firm.",
                    "The attack is powerful, but it crashes harmlessly against the solid defense of {target_name}. They stand their ground, refusing to yield a single inch.",
                    "{target_name} raises their defense, a solid, immovable object meeting an unstoppable force. The blow is stopped cold, though the effort costs them dearly in stamina."
                ],
                "fumble": [
                    "In the heat of battle, a foot slips on the uneven ground. {attacker_name} stumbles badly, their attack turning into a clumsy, flailing motion that poses no threat to anyone.",
                    "A moment of hesitation, a flicker of doubt, and the opening is lost. The attack from {attacker_name} is half-hearted and easily avoided, a clear sign of a lapse in focus.",
                    "The weapon feels alien and clumsy in their grip. {attacker_name} overextends wildly, the momentum of their own failed attack pulling them off balance and leaving them dangerously exposed."
                ]
            }

            #==================================================================
            # III. DAMAGE & CONSEQUENCE NARRATIVES (FALLBACK)
            #==================================================================
            self.damage_descriptions = {
                "light": [
                    "The blow lands, but it's a glancing one. It leaves a stinging, shallow cut on {target_name}, more of an insult than a serious injury.",
                    "It's a painful, but minor wound. The strike draws blood, but {target_name} is able to grit their teeth and fight through the sharp, localized pain.",
                    "The attack connects, but lacks true force. It's enough to make {target_name} hiss in annoyance and pain, but the injury is superficial."
                ],
                "moderate": [
                    "The impact tears through flesh and muscle with grim effect. A significant, freely-bleeding wound opens up on {target_name}, who staggers back from the shock and pain.",
                    "A deep gash is carved into {target_name}, a wound that will surely scar. They let out a sharp cry, their fighting stance faltering for a crucial second.",
                    "That one hurt. The blow lands with enough force to cause a substantial injury, and the expression on the face of {target_name} shifts from aggression to genuine distress."
                ],
                "heavy": [
                    "The weapon rends flesh and grates against bone with a sickening sound. It's a grievous wound that paints the ground crimson, nearly felling {target_name} where they stand.",
                    "The sheer, brutal impact drives the air from the lungs of {target_name}. The damage is devastating, leaving them pale and struggling to remain upright.",
                    "Catastrophic damage. The blow shatters the guard of {target_name} and their spirit in equal measure, leaving a ghastly wound that looks immediately life-threatening."
                ],
                "massive": [
                    "It's a bone-shattering impact, the sound of which echoes in the sudden silence. {target_name} is left reeling, their body overwhelmed by a degree of injury that seems impossible to survive.",
                    "The blow is catastrophic, a whirlwind of destructive force that obliterates defenses. {target_name} crumples to the ground, their lifeblood pooling beneath them.",
                    "This is a potentially fatal blow. The weapon strikes with such incredible force that {target_name} can only stare in shock at the horrific wound before their eyes roll back."
                ]
            }

            #==================================================================
            # IV. CONTEXTUAL & FINISHING NARRATIVES
            #==================================================================
            self.environmental_context = {
                "docks": [
                    "The scent of salt and bilge hangs heavy in the air, mingling with the fresh, metallic tang of blood.",
                    "A nearby stack of rotting crates collapses from a stray impact, showering the area in splinters and filth.",
                    "The thick, rolling fog from the bay swirls around the combatants, muffling the sounds of their struggle and giving the fight a ghostly, unreal quality."
                ],
                "alley": [
                    "The clash of combat echoes unnaturally between the grimy, narrow brick walls, making the fight sound larger and more chaotic than it is.",
                    "A stray blow smashes a grimy window pane, the sound of shattering glass a sharp counterpoint to the grunts of exertion.",
                    "The fight moves through a pile of refuse, the stench of garbage and decay filling the air as the combatants kick it aside."
                ],
                "tavern": [
                    "An overturned table becomes makeshift cover, splintering under a powerful blow. Patrons scream and flee for the exits, adding to the chaos.",
                    "Spilled ale and spirits make the wooden floor treacherous and slick. A fighter slips, barely recovering their footing in time to avoid a fatal mistake.",
                    "The flickering candlelight casts long, distorted shadows that writhe on the walls like demons, making it difficult to track the fluid movements of the fight."
                ],
                "chem_lab": [
                    "The acrid smell of volatile chemicals burns the nostrils, a constant, sharp reminder of the room's explosive potential.",
                    "A stray blow sends a rack of glowing vials crashing to the floor. The glass shatters, bathing the scene in an eerie, chem-luminescent light and releasing a cloud of noxious, choking fumes.",
                    "Intricate glass pipework and beakers rattle precariously with every heavy footstep and jarring impact, threatening to come crashing down at any moment."
                ],
                "rooftops": [
                    "The wind howls between the chem-stacks and clocktowers, a physical force that threatens to unbalance the fighters and send them plummeting into the chasm below.",
                    "Loose roof tiles skitter and slide underfoot, clattering down into the street hundreds of feet below with every desperate lunge and hasty retreat.",
                    "The glittering, indifferent lights of Piltover above and the neon-drenched haze of Zaun below form a dizzying, vertiginous backdrop to the life-or-death duel."
                ],
                "default": [
                    "The air itself seems to grow heavy, crackling with unspoken tension and the grim promise of violence.",
                    "Time stretches and compresses, each heartbeat a deafening drumbeat in the theater of battle, each action an eternity.",
                    "The combatants circle each other warily, a deadly dance of feints and probes as they search for the slightest weakness, the first mistake."
                ]
            }

            self.skill_flourishes = {
                "street_fighter": [
                    "True to their roots, {attacker_name} throws a bit of pocket sand towards {target_name}'s eyes before the attack.",
                    "Using a classic undercity trick, {attacker_name} feints a wild swing before delivering a sharp, precise jab."
                ],
                "intimidation": [
                    "A low growl rumbles in {attacker_name}'s chest as they advance, their very presence a weapon.",
                    "{attacker_name}'s cold, unwavering stare seems to momentarily freeze {target_name} in place."
                ]
            }
        
        def get_weapon_type(self, weapon_name):
            if not weapon_name: return "unarmed"
            weapon_lower = weapon_name.lower()
            if "puncher" in weapon_lower or "prosthetic" in weapon_lower: return "prosthetic_arm"
            if "knuckles" in weapon_lower: return "knuckles"
            if "sword" in weapon_lower or "blade" in weapon_lower: return "sword"
            if "dagger" in weapon_lower or "knife" in weapon_lower or "shiv" in weapon_lower: return "dagger"
            if "axe" in weapon_lower: return "axe"
            if "mace" in weapon_lower or "hammer" in weapon_lower: return "mace"
            if "staff" in weapon_lower or "rod" in weapon_lower: return "staff"
            return "default"

        def get_damage_category(self, damage_amount, target_max_hp):
            if target_max_hp <= 0: return "light"
            damage_ratio = damage_amount / target_max_hp
            if damage_ratio <= 0.15: return "light"
            if damage_ratio <= 0.35: return "moderate"
            if damage_ratio <= 0.60: return "heavy"
            return "massive"

        def get_pronoun(self, character, subject=True):
            return "they" if subject else "them"

        def get_location_context(self, node_id=None, environment="default"):
            """
            Enhanced location context using centralized locations.rpy system.
            Returns comprehensive environmental data for LLM prompts.
            """
            # Get location node from centralized system
            if node_id:
                location_node = get_location_by_node_id(node_id)
            elif environment != "default":
                # Try to find location by environment name
                location_node = get_location_by_node_id(environment.upper())
                if location_node.node_id == "UNKNOWN-UNKNOWN-UNKNOWN-UNKNOWN":
                    # Fallback: try current game state
                    location_node = get_current_location_node()
            else:
                # Get current location from game state
                location_node = get_current_location_node()
            
            # Return the pre-built combat context from the location node
            return location_node.get_combat_context()

        # --- ENHANCED METHOD ---
        def get_character_context(self, character):
            """Extract character description, backstory, fighting style, and pronouns for LLM context."""
            character_name = character.get_name() if hasattr(character, 'get_name') else str(character)
            
            # Check if this is a player character
            if hasattr(character, 'is_player') and character.is_player:
                # Default player pronouns - could be configurable in the future
                player_pronouns = getattr(character, 'pronouns', {'subject': 'they', 'object': 'them', 'possessive': 'their'})
                return {
                    'name': character_name,
                    'description': "A newcomer to Zaun's streets, still learning the harsh realities of the undercity",
                    'backstory': "Recently arrived in Zaun, fighting to survive and make a name for themselves",
                    'fighting_style': "Adaptive Fighter - still developing their combat style",
                    'gender': getattr(character, 'gender', 'unspecified'),
                    'pronouns': player_pronouns
                }
            
            # Look for character in NPC roster by checking all stat dictionaries
            for npc_id, npc_stats in default_npc_stats.items():
                if npc_stats.get('name', '').lower() == character_name.lower():
                    return {
                        'name': character_name,
                        'description': npc_stats.get('description', 'A combatant with unknown background'),
                        'backstory': npc_stats.get('backstory', 'Their history remains a mystery'),
                        'fighting_style': npc_stats.get('fighting_style', 'Unknown fighting style'),
                        'gender': npc_stats.get('gender', 'unspecified'),
                        'pronouns': npc_stats.get('pronouns', {'subject': 'they', 'object': 'them', 'possessive': 'their'})
                    }
            
            # Check dynamic NPCs if not found in static roster
            if hasattr(store, 'dynamic_npcs'):
                for dyn_id, dyn_npc in store.dynamic_npcs.items():
                    if hasattr(dyn_npc, 'name') and dyn_npc.name.lower() == character_name.lower():
                        dyn_pronouns = getattr(dyn_npc, 'pronouns', {'subject': 'they', 'object': 'them', 'possessive': 'their'})
                        return {
                            'name': character_name,
                            'description': getattr(dyn_npc, 'description', 'A fighter with unknown appearance'),
                            'backstory': getattr(dyn_npc, 'backstory', 'Their past is shrouded in mystery'),
                            'fighting_style': getattr(dyn_npc, 'fighting_style', 'Unknown combat approach'),
                            'gender': getattr(dyn_npc, 'gender', 'unspecified'),
                            'pronouns': dyn_pronouns
                        }
            
            # Fallback for unknown characters
            return {
                'name': character_name,
                'description': 'A mysterious combatant whose appearance tells little of their intentions',
                'backstory': 'A fighter whose past remains unknown',
                'fighting_style': 'Unpredictable Fighter - their methods are unclear',
                'gender': 'unspecified',
                'pronouns': {'subject': 'they', 'object': 'them', 'possessive': 'their'}
            }

        def generate_attack_narrative(self, attacker, target, hit_result, weapon_name=None, environment="default", node_id=None):
            """Generates a combat action description using LLM with character and location awareness."""
            attacker_name = attacker.get_name() if hasattr(attacker, 'get_name') else str(attacker)
            target_name = target.get_name() if hasattr(target, 'get_name') else str(target)
            
            # Get character context for both combatants
            attacker_context = self.get_character_context(attacker)
            target_context = self.get_character_context(target)
            
            # Get comprehensive location context from centralized location system
            location_data = self.get_location_context(node_id, environment)
            location_node = get_current_location_node() if not node_id else get_location_by_node_id(node_id)
            natural_subnode = location_node.get_natural_language_subnode() if location_node else "the area"
            
            # Build enhanced LLM prompt with character, location and environmental context
            attacker_pronouns = attacker_context['pronouns']
            target_pronouns = target_context['pronouns']
            
            prompt = (
                f"Describe a combat action in a fantasy setting with detailed character and environmental context.\n\n"
                f"COMBATANTS:\n"
                f"Attacker - {attacker_context['name']} ({attacker_context['gender']}): {attacker_context['description']} "
                f"Background: {attacker_context['backstory']} "
                f"Combat Style: {attacker_context['fighting_style']} "
                f"Pronouns: {attacker_pronouns['subject']}/{attacker_pronouns['object']}/{attacker_pronouns['possessive']}\n"
                f"Target - {target_context['name']} ({target_context['gender']}): {target_context['description']} "
                f"Background: {target_context['backstory']} "
                f"Combat Style: {target_context['fighting_style']} "
                f"Pronouns: {target_pronouns['subject']}/{target_pronouns['object']}/{target_pronouns['possessive']}\n\n"
                f"LOCATION: The fight takes place in {natural_subnode} within {location_data['location_specifics']}. "
                f"Setting: {location_data['regional_atmosphere']} in {location_data['district_details']}. "
                f"Environmental factors: {location_data['environmental_factors']}. "
                f"Combat hazards: {location_data['combat_implications']}.\n\n"
                f"ACTION: {attacker_name} uses a {weapon_name or 'unarmed attack'} against {target_name}. "
                f"Result: {hit_result}.\n\n"
                f"INSTRUCTIONS: Write a single, vivid paragraph describing this combat action. Incorporate the characters' backgrounds, "
                f"fighting styles, and personalities into how they fight. Use the correct pronouns for each character as specified above "
                f"({attacker_name}: {attacker_pronouns['subject']}/{attacker_pronouns['object']}/{attacker_pronouns['possessive']}, "
                f"{target_name}: {target_pronouns['subject']}/{target_pronouns['object']}/{target_pronouns['possessive']}). "
                f"Naturally weave in the environmental hazards and location characteristics. "
                f"Focus on how both the specific location ('{natural_subnode}') and the combatants' unique traits affect the fight. "
                f"Use descriptive, immersive language that brings both characters and setting to life. Avoid overusing 'they/them/their' "
                f"pronouns when more specific gendered pronouns are available. Do not add dialogue or conversational text."
            )

            # Attempt to get narration from the local LLM.
            llm_narrative = get_llm_narration(prompt)

            if llm_narrative:
                # If successful, return the AI-generated text.
                return llm_narrative.strip()

            # --- FALLBACK METHOD: Original Template System ---
            # If the LLM call fails (returns None), use the original template system as a backup.
            weapon_type = self.get_weapon_type(weapon_name)
            attack_intro_template = random.choice(self.weapon_attacks.get(weapon_type, self.weapon_attacks["default"]))
            narrative = attack_intro_template.format(attacker_name=attacker_name, target_name=target_name)

            if hit_result in ["critical", "hit"]:
                hit_result_template = random.choice(self.hit_results[hit_result])
                result_desc = hit_result_template.format(attacker_name=attacker_name, target_name=target_name)
                narrative += f" {result_desc}"

            elif hit_result == "miss":
                miss_type = random.choice(["dodge", "parry", "block"])
                miss_template = random.choice(self.miss_results[miss_type])
                result_desc = miss_template.format(target_name=target_name, attacker_name=attacker_name)
                narrative += f" {result_desc}"

            elif hit_result == "fumble":
                fumble_template = random.choice(self.miss_results["fumble"])
                result_desc = fumble_template.format(attacker_name=attacker_name, attacker_pronoun=self.get_pronoun(attacker, subject=False))
                narrative += f" {result_desc}"

            if random.random() < 0.3: # Chance for environmental context
                if environment in self.environmental_context:
                    env_context = random.choice(self.environmental_context[environment])
                    narrative += f" {env_context}"
            
            return narrative.strip()


        def generate_damage_narrative(self, target, damage_data):
            """Generates a separate prose line for the damage dealt."""
            if not target or not damage_data or damage_data.get('total', 0) <= 0:
                return None
            
            target_max_hp = getattr(target.character_data, 'max_hp', 20)
            damage_category = self.get_damage_category(damage_data.get('total', 0), target_max_hp)
            
            damage_desc_template = random.choice(self.damage_descriptions[damage_category])
            damage_desc = damage_desc_template.format(target_name=target.get_name())
            
            return f"{damage_desc}"

        def generate_finishing_blow_prose(self, actor_name, target_name, choice, weapon_name=None, location="underground_fight_club"):
            """Generates greatly expanded, cinematic prose for finishing blows."""
            location_descriptions = {
                "underground_fight_club": {
                    "setting": "the dirt-floored cistern of the fight club",
                    "atmosphere": ["The roar of the crowd falls to a hushed, bloodthirsty whisper, every eye fixed on the final, grim tableau.", "Dust motes dance in the single, harsh beam of light from above, illuminating the brutal finality of the moment.", "The air grows thick with the metallic scent of blood and the collective, held breath of the spectators."]
                },
                "default": {
                    "setting": "the battlefield",
                    "atmosphere": ["The chaotic sounds of battle seem to fade into a dull roar, the world narrowing to this single, final act of violence.", "Time itself seems to slow to a crawl, each ragged breath and frantic heartbeat suspended in the moment before the end.", "A grim, profound hush falls over the area. All that matters now is the choice between mercy and death."]
                }
            }
            
            loc_data = location_descriptions.get(location, location_descriptions["default"])
            atmosphere = random.choice(loc_data["atmosphere"])
            
            weapon_finishers = {
                "unarmed": {
                    "lethal": [
                        f"{atmosphere}. There is no weapon, only intent. {actor_name} moves with chilling finality, their hands becoming instruments of death. A single, brutally efficient strike to a vital point on {target_name} ends the conflict with a sickening, quiet snap.",
                        f"{atmosphere}. With the fight won, {actor_name} stands over their fallen foe. A quick, precise application of pressure to the throat of {target_name} ensures the silence is permanent. It is a grim, necessary act in this brutal world."
                    ],
                    "nonlethal": [
                        f"{atmosphere}. {actor_name} shows restraint, a quality rarer than gold in these parts. A carefully applied sleeper hold on {target_name} brings a swift and peaceful end to their struggles, their body going limp as consciousness fades.",
                        f"{atmosphere}. Instead of a final, killing blow, {actor_name} delivers a sharp, precise chop to the side of the neck. The eyes of {target_name} roll back as they slump to the ground, unconscious but alive."
                    ]
                },
                "default": {
                    "lethal": [
                        f"{atmosphere}. {actor_name} stands over the fallen {target_name}, their weapon poised and dripping. With cold resolve and a heavy heart, they deliver the killing blow, ending the battle permanently and irrevocably.",
                        f"{atmosphere}. There is no mercy to be found here. {actor_name} raises their weapon one last time, striking a decisive blow that ensures {target_name} will never threaten anyone again."
                    ],
                    "nonlethal": [
                        f"{atmosphere}. For a long moment, {actor_name} hesitates, the choice hanging heavy in the air. They choose mercy. The final strike is with the flat of the blade or the pommel, a concussive blow that knocks {target_name} unconscious but preserves their life.",
                        f"{atmosphere}. Compassion, or perhaps simple pragmatism, stays the hand of {actor_name}. They deliver a carefully measured non-fatal blow, allowing {target_name} to live and perhaps learn from their defeat."
                    ]
                }
            }
            # Add other weapon types by copying the 'default' structure
            weapon_finishers["sword"] = weapon_finishers["default"]
            weapon_finishers["dagger"] = weapon_finishers["default"]
            weapon_finishers["axe"] = weapon_finishers["default"]
            weapon_finishers["mace"] = weapon_finishers["default"]
            weapon_finishers["staff"] = weapon_finishers["default"]
            weapon_finishers["knuckles"] = weapon_finishers["unarmed"] # Similar feel
            weapon_finishers["prosthetic_arm"] = weapon_finishers["default"]


            weapon_type = self.get_weapon_type(weapon_name)
            finisher_type = "lethal" if choice == "lethal" else "nonlethal"
            return random.choice(weapon_finishers.get(weapon_type, weapon_finishers["default"])[finisher_type])

        def generate_event_prose(self, event):
            """Map events to appropriate narrative method."""
            event_type = event.get("event_type")
            
            if event_type == "attack_resolution":
                attacker = event.get("actor")
                target = event.get("target")
                if not attacker or not target: return None

                if event.get("is_critical_fumble"): hit_result = "fumble"
                elif event.get("is_critical_hit"): hit_result = "critical"
                elif event.get("hit"): hit_result = "hit"
                else: hit_result = "miss"
                
                weapon = event.get("weapon")
                weapon_name = weapon.name if weapon else None
                return self.generate_attack_narrative(attacker, target, hit_result, weapon_name)

            elif event_type == "damage_resolution":
                target = event.get("target")
                damage_data = {"total": event.get("total_damage", 0)}
                return self.generate_damage_narrative(target, damage_data)

            elif event_type == "combat_start":
                return "The battle begins! Turn order: " + ", ".join(event.get("turn_order", []))
            elif event_type == "round_start":
                return f"The brutal ballet continues as round {event.get('round_number', 1)} begins."
            elif event_type == "combat_end":
                victor_obj = next((p for p in event.get("participants", []) if getattr(p.character_data, 'is_player', False)), None)
                victor_char = victor_obj.character_data if victor_obj else None
                return f"The battle concludes. As the dust settles, {victor_char.name if victor_char else 'the victor'} emerges triumphant."
            
            return None

# Initialize global narrative generator
default combat_narrative_generator = CombatNarrativeGenerator()
