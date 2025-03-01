from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import math


class BunnyHopController(FirstPersonController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mouse_sensitivity = Vec2(40, 40)
        self.speed = 8
        self.height = 2
        self.jump_height = 2
        
        # Bunnyhopping specific variables
        self.original_speed = self.speed
        self.speed_multiplier = 1.0
        self.max_speed_multiplier = float('inf')
        self.per_hop_multiplier_amount = 0.25
        self.diminish_value = 0.05  # Regular diminishing rate
        self.long_distance_diminish = 0.01  # Lower diminishing rate for long-distance travel
        self.jump_cooldown = 0
        self.jump_cooldown_max = 0.2
        
        # Jump state tracking
        self.was_grounded = True
        self.jump_count = 0
        self.last_jump_time = 0
        
        # For calculating speed display
        self.last_position = Vec3(self.position)
        self.velocity = Vec3(0, 0, 0)
        self.bhop_enabled = False
        
        # For handling long-distance travel
        self.distance_traveled = 0
        self.long_distance_mode = False

    def update(self):
        # Always let parent update run first for physics and camera movement
        super().update()
        
        # Calculate velocity for display
        self.velocity = self.position - self.last_position
        self.last_position = Vec3(self.position.x, self.position.y, self.position.z)
        
        # Update distance traveled (only horizontal distance)
        horizontal_velocity = Vec2(self.velocity.x, self.velocity.z)
        self.distance_traveled += horizontal_velocity.length()
        
        # Switch to long-distance mode if player has traveled far
        self.long_distance_mode = self.distance_traveled > 500
        
        # Update jump cooldown
        if self.jump_cooldown > 0:
            self.jump_cooldown -= time.dt
        
        # Track landing for combo jumps
        if not self.was_grounded and self.grounded:
            # Just landed
            self.jump_cooldown = 0  # Allow immediate jump on landing for combos
        
        # Handle bunnyhopping
        if held_keys['space']:
            # Enable bunnyhopping mode
            self.bhop_enabled = True
            
            # Jump if grounded and cooldown is over
            if self.grounded and self.jump_cooldown <= 0:
                self.jump()
                self.jump_cooldown = self.jump_cooldown_max
                self.last_jump_time = time.time()
                self.jump_count += 1
                
                # Increase multiplier - higher boost for consecutive jumps
                if self.jump_count > 1:
                    # Bonus for consecutive jumps
                    self.speed_multiplier = min(self.max_speed_multiplier, 
                                              self.speed_multiplier + self.per_hop_multiplier_amount)
                else:
                    # First jump bonus is smaller
                    self.speed_multiplier = min(self.max_speed_multiplier,
                                              self.speed_multiplier + self.per_hop_multiplier_amount * 0.5)
            
            # Apply speed boost every frame while bunnyhopping with movement
            if any(held_keys[key] for key in ['w', 'a', 's', 'd']):
                self.apply_speed_boost()
        else:
            self.bhop_enabled = False
            self.jump_count = 0  # Reset jump count if space released
            
        # Reset jump count if on ground too long without jumping
        if self.grounded and time.time() - self.last_jump_time > 0.5:
            self.jump_count = 0
            
        # Gradually decrease speed multiplier when not bunnyhopping or not moving
        if (not self.bhop_enabled or not any(held_keys[key] for key in ['w', 'a', 's', 'd'])) and self.speed_multiplier > 1.0:
            # Use different diminish rates for long-distance travel
            diminish_rate = self.long_distance_diminish if self.long_distance_mode else self.diminish_value
            self.speed_multiplier = max(1.0, self.speed_multiplier - diminish_rate * time.dt)
        
        # Update grounded state
        self.was_grounded = self.grounded
    
    def apply_speed_boost(self):
        """Apply extra velocity based on direction and speed multiplier"""
        # Get movement direction
        move_direction = self.get_movement_direction()
        if move_direction.length() > 0:
            # Calculate boosted movement - apply full multiplier for better feel
            extra_speed = move_direction * self.original_speed * (self.speed_multiplier - 1.0) * time.dt * 1.5
            # Apply the extra speed by updating position
            self.position += extra_speed
    
    def get_movement_direction(self):
        """Calculate the movement direction based on key inputs"""
        move_direction = Vec3(0, 0, 0)
        if held_keys['w']: move_direction += Vec3(0, 0, 1)
        if held_keys['s']: move_direction += Vec3(0, 0, -1)
        if held_keys['a']: move_direction += Vec3(-1, 0, 0)
        if held_keys['d']: move_direction += Vec3(1, 0, 0)
        
        if move_direction.length() > 0:
            move_direction = move_direction.normalized()
            # Apply rotation to move in the direction the player is facing
            move_direction = Vec3(
                move_direction.x * math.cos(math.radians(-self.rotation_y)) - move_direction.z * math.sin(math.radians(-self.rotation_y)),
                0,
                move_direction.x * math.sin(math.radians(-self.rotation_y)) + move_direction.z * math.cos(math.radians(-self.rotation_y))
            )
        
        return move_direction 