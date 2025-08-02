# Discovery Path Scene - Travel from Crashpad to Tavern
# This scene takes the player through 4 locations with different discovery levels

label discovery_path_journey:
    "You decide to make your way from the Industrial Crashpad to the Lanes Tavern, taking a route through some lesser-known areas of Zaun."
    
    # Starting location - CRASHPAD
    $ current_location = "ZAUN-INDUSTRIALZONE-CRASHPAD-MAIN"
    scene bg_zaun_industrial
    "You stand in the makeshift shelter of the Industrial Crashpad, surrounded by improvised furniture and the dim glow of jury-rigged lamps."
    "The cramped conditions and scrap metal walls remind you of the harsh realities of life in Zaun's industrial zones."
    
    menu:
        "Ready to begin your journey?"
        "Yes, let's go":
            pass
        "Let me prepare first":
            "You take a moment to gather your thoughts and check your equipment."
    
    # Location 1 - Empty discovery level
    $ current_location = "ZAUN-INDUSTRIALZONE-SCRAP_YARD-EMPTY_SECTION"
    scene bg_zaun_scrapyard
    "You make your way to a barren section of the scrap yard that appears to have been picked completely clean."
    "Empty metal frameworks stretch before you, with scattered rust flakes dancing in the wind that whistles through the hollow structures."
    "The sharp edges of discarded metal glint dangerously in the dim light, and your footing feels uncertain on the loose scrap beneath your feet."
    
    menu:
        "This area looks thoroughly scavenged. What do you want to do?"
        "Search for anything useful" if True:
            "You spend some time carefully examining the area, but as expected, there's nothing of value left to find."
            "The previous scavengers were thorough - this section is truly empty."
        "Move on quickly":
            "You decide not to waste time in this barren area and continue on your path."
    
    # Location 2 - Normal discovery level  
    $ current_location = "ZAUN-INDUSTRIALZONE-MAINTENANCE_TUNNEL-CONNECTING_PASSAGE"
    scene bg_zaun_tunnel
    "You enter a narrow maintenance tunnel that connects different sections of the industrial zone."
    "Exposed pipes and cables run along the walls, while dim emergency lighting casts long shadows down the cramped passage."
    "Your footsteps echo in the confined space, and you notice exposed electrical hazards and condensation dripping from overhead pipes."
    
    menu:
        "The tunnel seems to have some potential for discovery. What do you do?"
        "Search the maintenance areas" if True:
            "You carefully examine the maintenance equipment and pipe junctions."
            "This area shows promise - maintenance tunnels often contain forgotten tools and spare parts."
        "Press forward cautiously":
            "You move carefully through the tunnel, mindful of the electrical hazards and low ceiling."
    
    # Location 3 - Rare discovery level
    $ current_location = "ZAUN-ENTRESOLS-ABANDONED_WORKSHOP-STORAGE_ROOM"
    scene bg_zaun_workshop
    "You discover an abandoned workshop's storage room, filled with dust-covered workbenches and shelves of forgotten parts."
    "Filtered light streams through grimy windows, illuminating the valuable salvage cluttered throughout the space."
    "The shelving looks unstable, and dust motes dance in the air, but you can see this place contains some genuinely useful items."
    
    menu:
        "This storage room looks promising! How do you approach it?"
        "Carefully search the shelves" if True:
            "You methodically examine the shelves, being careful not to disturb the unstable stacking."
            "Your patience pays off - this room contains some rare components that previous scavengers missed."
        "Quick grab and go":
            "You quickly snatch a few visible items and retreat before the unstable shelving can collapse."
    
    # Location 4 - Epic discovery level
    $ current_location = "ZAUN-ENTRESOLS-HIDDEN_CACHE-SECRET_CHAMBER"
    scene bg_zaun_cache
    "You stumble upon something extraordinary - a concealed chamber that appears to be a hidden cache from before the wars."
    "Pristine pre-war equipment gleams in the soft blue glow emanating from hextech remnants that have remained untouched by time."
    "The delicate ancient machinery hums softly, and you realize you've found something truly valuable and rare."
    
    menu:
        "This is an incredible find! How do you proceed?"
        "Carefully examine everything" if True:
            "You spend considerable time documenting and carefully extracting the most valuable items."
            "This cache represents a once-in-a-lifetime discovery - pre-war artifacts of immense value."
        "Take what you can quickly":
            "You hastily gather what appears most valuable, worried that someone else might discover this place."
    
    # Final destination - TAVERN
    $ current_location = "ZAUN-LANES-TAVERN-MAIN_ROOM"
    scene bg_zaun_tavern
    "Finally, you arrive at the Lanes Tavern, your journey complete."
    "The dimly lit drinking establishment buzzes with the voices of local workers, heavy wooden furniture scattered throughout."
    "Flickering oil lamps cast dancing shadows on the walls, and the wooden floors show stains from countless spilled drinks."
    "You've successfully navigated from the Industrial Crashpad through four distinct areas, each offering different opportunities for discovery."
    
    menu:
        "You've completed your journey through the discovery path. What now?"
        "Order a drink and rest":
            "You settle into the tavern atmosphere, reflecting on your journey and the discoveries you made along the way."
        "Plan your next move":
            "You use this time to organize your findings and plan your next expedition through Zaun's hidden paths."
    
    "Your journey through the discovery path is complete. Each location offered its own unique challenges and opportunities."
    
    return

# Optional: Quick test label to jump directly to this scene
label test_discovery_path:
    jump discovery_path_journey
