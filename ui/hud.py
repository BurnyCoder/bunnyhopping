from ursina import *


class HUD:
    def __init__(self, player, environment):
        self.player = player
        self.environment = environment
        
        # Create HUD elements
        self.create_instructions()
        self.create_speed_display()
        self.create_distance_display()
        
        # For speed calculation
        self.displayed_speed = 0
        
        # Create updater entity
        self.updater = Entity()
        self.updater.update = self.update_hud
    
    def create_instructions(self):
        """Create instruction text display."""
        self.instructions = Text(
            text="WASD to move, HOLD SPACE to bunnyhop continuously",
            origin=(0, 0),
            position=(0, 0.4),
            color=color.white
        )
    
    def create_speed_display(self):
        """Create speed display text."""
        self.speed_text = Text(
            text="Speed: 0 | Multiplier: 1.0x",
            origin=(0, 0),
            position=(0, 0.35),
            color=color.yellow
        )
    
    def create_distance_display(self):
        """Create distance display text."""
        self.distance_text = Text(
            text="Distance: 0 meters",
            origin=(0, 0),
            position=(0, 0.3),
            color=color.white
        )
    
    def update_hud(self):
        """Update all HUD elements."""
        self.update_speed()
        self.update_distance()
    
    def update_speed(self):
        """Update the speed display with current player velocity."""
        # Calculate horizontal speed (ignoring vertical movement)
        horizontal_velocity = Vec2(self.player.velocity.x, self.player.velocity.z)
        
        # Calculate speed - use a better scaling factor based on the original player speed
        speed_factor = 50 / self.player.original_speed  # Normalize to make display more intuitive
        raw_speed = horizontal_velocity.length() * speed_factor
        
        # Apply smoothing for better display
        self.displayed_speed = lerp(self.displayed_speed, raw_speed, time.dt * 5)
            
        # Round for display
        speed = round(self.displayed_speed, 1)
        multiplier = round(self.player.speed_multiplier, 2)
        
        # Set color based on multiplier (green to yellow to red as speed increases)
        # Cap color changes at 10x
        capped_multiplier = min(10.0, self.player.speed_multiplier)
        normalized_multiplier = (capped_multiplier - 1.0) / 9.0  # Range 1.0 to 10.0 maps to 0.0 to 1.0
        
        speed_color = color.rgb(
            255 * min(1, normalized_multiplier * 2),  # Red increases faster
            255 * max(0, 1 - normalized_multiplier),  # Green decreases as we go faster
            0  # No blue
        )
        
        # Update the text
        self.speed_text.text = f"Speed: {speed} | Multiplier: {multiplier}x"
        self.speed_text.color = speed_color
    
    def update_distance(self):
        """Update the distance display."""
        # Get distance from start
        distance_meters = round(self.environment.get_distance_from_start(), 1)
        
        # Update display
        self.distance_text.text = f"Distance: {distance_meters} meters"
        
        # Change color based on distance milestones
        if distance_meters > 1000:
            self.distance_text.color = color.rgb(255, 215, 0)  # Gold color
        elif distance_meters > 500:
            self.distance_text.color = color.rgb(192, 192, 192)  # Silver color
        elif distance_meters > 100:
            self.distance_text.color = color.rgb(205, 127, 50)  # Bronze color
        else:
            self.distance_text.color = color.white 