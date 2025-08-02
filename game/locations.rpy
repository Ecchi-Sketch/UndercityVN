#============================================================================
# CENTRALIZED LOCATION DEFINITIONS FOR NODE-BASED MAPPING SYSTEM
#============================================================================
# This file contains all location data for the node-based mapping system.
# It provides a single source of truth for location information used across
# combat narratives, character sheets, and future map implementations.
# 
# Node ID Format: REGION-DISTRICT-LOCATION-SUBNODE
# Example: PILTOVER-MIDTOWN-ACADEMY_UNIFORM_SERVICE-SIDE_ROOM
#============================================================================
# Set current location
# $ store.current_node_id = "ZAUN-INDUSTRIALZONE-CHEMTECH_FOUNDRY-MIXING_CHAMBER"


init python:
    class LocationNode:
        """
        Represents a single location node in the mapping system.
        Contains all contextual information needed for display, combat, and navigation.
        """
        def __init__(self, node_id, display_name, region, district, location, subnode=None):
            self.node_id = node_id
            self.display_name = display_name
            self.region = region
            self.district = district 
            self.location = location
            self.subnode = subnode
            
            # Descriptive information
            self.description = ""
            self.atmosphere = ""
            self.environmental_factors = ""
            self.combat_implications = ""
            
            # Regional and district context (will be populated from regional data)
            self.regional_atmosphere = ""
            self.district_details = ""
            
            # Discovery system properties
            self.discovery_level = "normal"  # "empty", "normal", "rare", "epic"
            self.discovery_ranges = {
                "normal": (10, 15),
                "rare": (16, 19),
                "epic": (20, 20)
            }
            self.discovery_attempts = 0
            self.discovery_cooldown = 0
            
        def set_details(self, description, atmosphere, environmental_factors, combat_implications):
            """Set the detailed information for this location."""
            self.description = description
            self.atmosphere = atmosphere
            self.environmental_factors = environmental_factors
            self.combat_implications = combat_implications
            return self
            
        def set_regional_context(self, regional_atmosphere, district_details):
            """Set regional and district context information."""
            self.regional_atmosphere = regional_atmosphere
            self.district_details = district_details
            return self
            
        def set_discovery_properties(self, discovery_level="normal", custom_ranges=None):
            """Set discovery properties for this location."""
            self.discovery_level = discovery_level
            if custom_ranges:
                self.discovery_ranges = custom_ranges
            return self
            
        def get_formatted_display(self):
            """
            Returns a formatted display string for the character sheet.
            Format: "Region > District > Location > Subnode"
            """
            components = []
            if self.region: components.append(self.region.title())
            if self.district: components.append(self.district.replace('_', ' ').title())
            if self.location: components.append(self.location.replace('_', ' ').title())
            if self.subnode: components.append(self.subnode.replace('_', ' ').title())
            
            return " > ".join(components)
            
        def get_combat_context(self):
            """
            Returns comprehensive combat context data for LLM prompts.
            """
            return {
                'node_id': self.node_id,
                'full_description': f"node {self.node_id}: {self.subnode.replace('_', ' ').lower() if self.subnode else 'the area'} within {self.description} in {self.district_details} of {self.regional_atmosphere}",
                'regional_atmosphere': self.regional_atmosphere,
                'district_details': self.district_details,
                'location_specifics': self.description,
                'environmental_factors': self.environmental_factors,
                'combat_implications': self.combat_implications
            }
            
        def get_short_description(self):
            """Returns a concise description suitable for quick reference."""
            return f"{self.display_name}: {self.description}"
            
        def get_natural_language_subnode(self):
            """
            Converts the subnode to natural language for LLM prompts.
            Examples: 'MIXING_CHAMBER' -> 'the Mixing Chamber'
                     'MAIN_FLOOR' -> 'the Main Floor'
                     'SIDE_ROOM' -> 'a Side Room'
            """
            if not self.subnode:
                return "the area"
                
            # Convert underscores to spaces and title case
            natural = self.subnode.replace('_', ' ').title()
            
            # Add appropriate article based on subnode type
            if any(word in natural.lower() for word in ['room', 'chamber', 'floor', 'hall', 'area', 'office', 'workshop']):
                return f"the {natural}"
            elif any(word in natural.lower() for word in ['entrance', 'exit', 'passage']):
                return f"the {natural}"
            else:
                # Default to 'the' for most locations
                return f"the {natural}"

    # =======================================================================
    # REGIONAL DEFINITIONS
    # =======================================================================
    
    REGIONS = {
        "PILTOVER": {
            "display_name": "Piltover",
            "atmosphere": "the gleaming upper city of progress and innovation, with pristine streets, towering academies, and advanced hextech machinery",
            "districts": {
                "MIDTOWN": {
                    "display_name": "Midtown",
                    "details": "the bustling commercial heart with academies, shops, and administrative buildings"
                },
                "ACADEMY_QUARTER": {
                    "display_name": "Academy Quarter", 
                    "details": "the prestigious educational district with grand halls and research facilities"
                },
                "HARBOR_DISTRICT": {
                    "display_name": "Harbor District",
                    "details": "the trading hub where goods flow between Piltover and the world beyond"
                }
            }
        },
        "ZAUN": {
            "display_name": "Zaun",
            "atmosphere": "the underground city of industry and chemical innovation, filled with toxic fumes, mechanical wonders, and cramped industrial districts",
            "districts": {
                "INDUSTRIALZONE": {
                    "display_name": "Industrial Zone",
                    "details": "the heavy manufacturing sector with foundries, workshops, and chemical plants"
                },
                "ENTRESOLS": {
                    "display_name": "Entresols",
                    "details": "the working districts where most production happens, cramped and dangerous"
                },
                "LANES": {
                    "display_name": "The Lanes",
                    "details": "the residential and commercial areas where most citizens live and work"
                },
                "UNDERCITY": {
                    "display_name": "Undercity",
                    "details": "the deepest levels filled with abandoned machinery and forgotten passages"
                }
            }
        }
    }
    
    # =======================================================================
    # LOCATION DATABASE - All Known Nodes
    # =======================================================================
    
    def create_location_database():
        """Creates and populates the complete location database."""
        db = {}
        
        # Helper function to create and register a location
        def add_location(node_id, display_name, description, atmosphere, env_factors, combat_impl):
            parts = node_id.split('-')
            region = parts[0] if len(parts) > 0 else ""
            district = parts[1] if len(parts) > 1 else ""
            location = parts[2] if len(parts) > 2 else ""
            subnode = parts[3] if len(parts) > 3 else None
            
            # Get regional context
            region_data = REGIONS.get(region, {})
            district_data = region_data.get("districts", {}).get(district, {})
            
            regional_atmosphere = region_data.get("atmosphere", "an unknown region")
            district_details = district_data.get("details", "an unknown district")
            
            node = LocationNode(node_id, display_name, region, district, location, subnode)
            node.set_details(description, atmosphere, env_factors, combat_impl)
            node.set_regional_context(regional_atmosphere, district_details)
            
            db[node_id] = node
            return node
        
        # =======================================================================
        # PILTOVER LOCATIONS
        # =======================================================================
        
        add_location(
            "PILTOVER-MIDTOWN-ACADEMY_UNIFORM_SERVICE-MAIN_SHOP",
            "Academy Uniform Service - Main Shop",
            "a formal tailoring shop serving Piltover Academy students",
            "pristine displays of academic regalia, precise measurements, formal atmosphere",
            "confined spaces between fabric racks, scattered measuring tools, formal constraints",
            "limited mobility between displays, potential improvised weapons from tailoring tools, fabric could muffle sounds"
        )
        
        add_location(
            "PILTOVER-MIDTOWN-ACADEMY_UNIFORM_SERVICE-SIDE_ROOM",
            "Academy Uniform Service - Storage Room", 
            "a cramped storage area filled with fabric rolls and measuring equipment",
            "cluttered storage space, bolt of fine fabrics, dim lighting from single hextech lamp",
            "very confined space, fabric rolls creating maze-like layout, measuring equipment scattered about",
            "extremely limited mobility, fabric rolls as obstacles or cover, measuring tools as improvised weapons"
        )
        
        add_location(
            "PILTOVER-MIDTOWN-HEXTECH_WORKSHOP-MAIN_FLOOR",
            "Hextech Workshop - Main Floor",
            "a gleaming workshop filled with hextech crystals and precision instruments",
            "blue-white glow from active hexcrystals, humming machinery, sterile work environment",
            "delicate hextech equipment, unstable crystal formations, electromagnetic fields",
            "risk of hextech discharge, delicate equipment as hazards, crystal shards as weapons"
        )
        
        # =======================================================================
        # ZAUN LOCATIONS  
        # =======================================================================
        
        add_location(
            "ZAUN-INDUSTRIALZONE-CHEMTECH_FOUNDRY-MIXING_CHAMBER",
            "Chemtech Foundry - Mixing Chamber",
            "a facility producing volatile chemical compounds and mechanical parts",
            "bubbling chemical vats, toxic green fumes, unstable walkways over processing equipment",
            "volatile chemicals everywhere, poor ventilation, unstable metal grating walkways",
            "chemical hazards from spills, potential explosions, poor footing on metal grating, toxic atmosphere affecting breathing"
        )
        
        add_location(
            "ZAUN-INDUSTRIALZONE-CHEMTECH_FOUNDRY-MAIN_FLOOR", 
            "Chemtech Foundry - Main Floor",
            "the primary production floor of a chemical manufacturing facility",
            "massive chemical vats, conveyor systems, workers in protective gear",
            "heavy industrial machinery, chemical storage tanks, steam and toxic vapors",
            "heavy machinery as obstacles, chemical spills creating hazardous terrain, steam obscuring vision"
        )
        
        add_location(
            "ZAUN-INDUSTRIALZONE-CRASHPAD-MAIN",
            "Industrial Crashpad - Main Area",
            "a makeshift shelter constructed from scrap metal and salvaged materials",
            "improvised furniture from salvaged parts, dim lighting from jury-rigged lamps, crowded conditions",
            "scrap metal walls, unstable improvised structures, poor lighting, cramped living space",
            "debris and salvage as improvised weapons, unstable structures that could collapse, poor visibility"
        )
        
        # Path from CRASHPAD to TAVERN - 4 intermediate locations with different discovery levels
        add_location(
            "ZAUN-INDUSTRIALZONE-SCRAP_YARD-EMPTY_SECTION",
            "Scrap Yard - Empty Section",
            "a barren section of the scrap yard that has been picked clean",
            "empty metal frameworks, scattered rust flakes, wind whistling through hollow structures",
            "unstable metal debris, sharp edges everywhere, poor footing on loose scrap",
            "sharp metal debris as weapons, unstable footing, potential cuts from rusty edges"
        ).set_discovery_properties("empty")
        
        add_location(
            "ZAUN-INDUSTRIALZONE-MAINTENANCE_TUNNEL-CONNECTING_PASSAGE",
            "Maintenance Tunnel - Connecting Passage",
            "a narrow maintenance tunnel connecting different industrial sections",
            "exposed pipes and cables, dim emergency lighting, echoing footsteps",
            "cramped spaces, exposed electrical hazards, dripping condensation",
            "limited mobility in narrow space, electrical hazards, pipes as cover or weapons"
        ).set_discovery_properties("normal")
        
        add_location(
            "ZAUN-ENTRESOLS-ABANDONED_WORKSHOP-STORAGE_ROOM",
            "Abandoned Workshop - Storage Room",
            "a forgotten storage room filled with old tools and rare components",
            "dust-covered workbenches, shelves of forgotten parts, filtered light through grimy windows",
            "cluttered with valuable salvage, unstable shelving, poor visibility from dust",
            "abundant improvised weapons from tools, falling shelves as hazards, dust clouds obscuring vision"
        ).set_discovery_properties("rare")
        
        add_location(
            "ZAUN-ENTRESOLS-HIDDEN_CACHE-SECRET_CHAMBER",
            "Hidden Cache - Secret Chamber",
            "a concealed chamber containing valuable pre-war artifacts and rare materials",
            "pristine pre-war equipment, soft blue glow from hextech remnants, untouched by time",
            "delicate ancient machinery, valuable artifacts, unstable hextech energy",
            "fragile valuable equipment, potential hextech discharge, ancient weapons as rare finds"
        ).set_discovery_properties("epic")
        
        add_location(
            "ZAUN-ENTRESOLS-WORKSHOP-MAIN_FLOOR",
            "Entresols Workshop - Main Floor", 
            "a mechanical workshop filled with tools and half-built inventions",
            "scattered tools and parts, oil-stained work surfaces, hissing steam from pipes",
            "mechanical debris everywhere, oil making surfaces slippery, hot steam from damaged pipes",
            "abundant improvised weapons from tools, slippery oil creating movement hazards, hot steam causing burns"
        )
        
        add_location(
            "ZAUN-LANES-TAVERN-MAIN_ROOM",
            "The Lanes Tavern - Main Room",
            "a dimly lit drinking establishment serving the local workers",
            "heavy wooden furniture, flickering oil lamps, rowdy atmosphere with shouting patrons",
            "wooden floors slippery from spills, heavy furniture throughout, poor lighting conditions",
            "slippery floors from spilled drinks, heavy chairs and tables as weapons or obstacles, poor lighting affecting accuracy"
        )
        
        add_location(
            "ZAUN-UNDERCITY-ABANDONED_TUNNEL-MAIN_PASSAGE",
            "Abandoned Tunnel - Main Passage",
            "a forgotten maintenance tunnel deep in Zaun's lowest levels",
            "dripping water, rusted pipes, emergency lighting casting eerie shadows",
            "wet surfaces, unstable ceiling supports, scattered debris, echoing acoustics",
            "slippery wet surfaces, potential cave-ins from unstable supports, debris as weapons, sound echoing reveals position"
        )
        
        # =======================================================================
        # GENERIC/FALLBACK LOCATIONS
        # =======================================================================
        
        add_location(
            "UNKNOWN-UNKNOWN-UNKNOWN-UNKNOWN",
            "Unknown Location",
            "an unspecified location",
            "mysterious and undefined characteristics",
            "standard environmental conditions",
            "typical combat conditions with no special hazards"
        )
        
        return db
    
    # Create the global location database
    LOCATION_DATABASE = create_location_database()
    
    def reset_all_discovery_attempts():
        """Reset discovery attempts for all locations - called on new game start"""
        for location_node in LOCATION_DATABASE.values():
            location_node.discovery_attempts = 0
            location_node.discovery_cooldown = 0
    
    # =======================================================================
    # LOCATION UTILITY FUNCTIONS
    # =======================================================================
    
    def get_location_by_node_id(node_id):
        """
        Retrieves a location node by its ID.
        Returns the location node or a fallback if not found.
        """
        if not node_id:
            return LOCATION_DATABASE.get("UNKNOWN-UNKNOWN-UNKNOWN-UNKNOWN")
            
        # Try exact match first
        if node_id in LOCATION_DATABASE:
            return LOCATION_DATABASE[node_id]
            
        # Try partial matches for incomplete node IDs
        components = str(node_id).split('-')
        
        # Try to find best partial match
        for full_node_id, location in LOCATION_DATABASE.items():
            full_components = full_node_id.split('-')
            match = True
            
            for i, component in enumerate(components):
                if i >= len(full_components) or component.upper() != full_components[i].upper():
                    match = False
                    break
                    
            if match:
                return location
                
        # Return fallback if no matches found
        return LOCATION_DATABASE.get("UNKNOWN-UNKNOWN-UNKNOWN-UNKNOWN")
    
    def get_current_location_node():
        """
        Gets the current location node from game state.
        Tries multiple possible game state variables.
        """
        try:
            # Try primary location variables
            if hasattr(store, 'current_node_id') and store.current_node_id:
                return get_location_by_node_id(store.current_node_id)
            elif hasattr(store, 'current_location') and store.current_location:
                return get_location_by_node_id(store.current_location)
            else:
                return get_location_by_node_id("UNKNOWN-UNKNOWN-UNKNOWN-UNKNOWN")
                
        except (AttributeError, NameError):
            return get_location_by_node_id("UNKNOWN-UNKNOWN-UNKNOWN-UNKNOWN")
    
    def get_locations_in_region(region_name):
        """Returns all location nodes in a specific region."""
        region_upper = region_name.upper()
        return [loc for loc in LOCATION_DATABASE.values() if loc.region == region_upper]
    
    def get_locations_in_district(region_name, district_name):
        """Returns all location nodes in a specific district."""
        region_upper = region_name.upper()
        district_upper = district_name.upper()
        return [loc for loc in LOCATION_DATABASE.values() 
                if loc.region == region_upper and loc.district == district_upper]

# =======================================================================
# GLOBAL ACCESS FUNCTIONS (for easy access from other files)
# =======================================================================

# Make key functions available globally
define location_db = LOCATION_DATABASE
