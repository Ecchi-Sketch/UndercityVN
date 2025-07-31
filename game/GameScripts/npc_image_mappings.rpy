# NPC to Image Association System
# Maps NPCs from NPCRoster.rpy to their corresponding character images

# Default image mapping for NPCs and characters
default npc_image_mappings = {
    # Main Characters
    "zev": "images/characters/zev_combat.png",
    "sevika": "images/characters/sevika_combat.png",
    
    # Enemy Types
    "zaunite_thug_template": "images/enemies/zaunite_thug.png",
    "street_tough": "images/enemies/street_tough.png",
    
    # Fallback images for generated NPCs
    "default_enemy": "images/enemies/default_enemy.png",
    "default_ally": "images/characters/default_ally.png",
    
    # Ultimate fallback image when all else fails
    "default_combat": "images/default_combat_img.png"
}

# Combat pose variants (for different combat states)
default combat_pose_variants = {
    "attacking": "_attack",
    "defending": "_defend", 
    "hurt": "_hurt",
    "idle": ""  # Default pose
}

init python:
    def get_character_image(character_name, pose="idle", fallback=True):
        """
        Get the appropriate image for a character in combat
        
        Parameters:
        - character_name: The name/ID of the character
        - pose: Combat pose variant ("attacking", "defending", "hurt", "idle")
        - fallback: Whether to use fallback images if specific image not found
        
        Returns:
        - String path to image file, or None if not found
        """
        # Get base image path
        base_image = npc_image_mappings.get(character_name.lower())
        
        if not base_image:
            # Try to match by character type or template
            for key in npc_image_mappings:
                if key in character_name.lower():
                    base_image = npc_image_mappings[key]
                    break
        
        if not base_image and fallback:
            # Use default fallback based on character role
            if character_name == "player" or character_name in ["zev", "sevika"]:
                base_image = npc_image_mappings.get("default_ally")
            else:
                base_image = npc_image_mappings.get("default_enemy")
        
        # Ultimate fallback to default_combat_img if still no image found
        if not base_image and fallback:
            base_image = npc_image_mappings.get("default_combat")
        
        if base_image:
            # Add pose variant if available
            pose_suffix = combat_pose_variants.get(pose, "")
            if pose_suffix:
                # Insert pose before file extension
                name, ext = base_image.rsplit('.', 1)
                variant_image = f"{name}{pose_suffix}.{ext}"
                
                # Check if variant exists, otherwise use base
                try:
                    # In production, you'd check if file exists
                    # For now, return variant path
                    return variant_image
                except:
                    return base_image
            else:
                return base_image
        
        return None
    
    def get_combat_image_dimensions(panel_width=580):
        """
        Calculate image dimensions for 3:5 aspect ratio scaled to panel width
        
        Parameters:
        - panel_width: Width of the panel containing the image
        
        Returns:
        - Tuple of (width, height) for the image
        """
        # 3:5 aspect ratio means height = width * (5/3)
        width = panel_width - 20  # Account for padding
        height = int(width * (5.0/3.0))
        
        return (width, height)
    
    def get_character_combat_info(character):
        """
        Get combat-relevant information for image display
        
        Parameters:
        - character: Character object with stats
        
        Returns:
        - Dictionary with character info for display
        """
        if not character:
            return None
            
        return {
            "name": getattr(character, 'name', 'Unknown'),
            "hp": getattr(character, 'hp', 0),
            "max_hp": getattr(character, 'max_hp', getattr(character, 'hp', 0)),
            "ac": getattr(character, 'ac', 10),
            "image": get_character_image(getattr(character, 'name', 'default_enemy'))
        }
