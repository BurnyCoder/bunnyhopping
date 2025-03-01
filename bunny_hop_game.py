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
        self.max_speed_multiplier = 3.0
        self.per_hop_multiplier_amount = 0.25
        self.diminish_value = 0.05
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

    def update(self):
        # Always let parent update run first for physics and camera movement
        super().update()
        
        # Calculate velocity for display
        self.velocity = self.position - self.last_position
        self.last_position = Vec3(self.position.x, self.position.y, self.position.z)
        
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
            self.speed_multiplier = max(1.0, self.speed_multiplier - self.diminish_value * time.dt)
        
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


class Game:
    def __init__(self):
        # Initialize the Ursina app
        self.app = Ursina()
        
        # Basic scene setup
        window.title = "Bunnyhop 3D"
        window.borderless = False
        window.exit_button.visible = False
        window.fps_counter.enabled = True
        
        # Create simple environment
        self.create_environment()
        
        # Add player with bunnyhop controller
        self.player = BunnyHopController(
            position=Vec3(0, 2, 0),
            collider='box',
            speed=8
        )
        
        # Instructions text
        self.instructions = Text(
            text="WASD to move, HOLD SPACE to bunnyhop continuously",
            origin=(0, 0),
            position=(0, 0.4),
            color=color.white
        )
        
        # Speed and multiplier display
        self.speed_text = Text(
            text="Speed: 0 | Multiplier: 1.0x",
            origin=(0, 0),
            position=(0, 0.35),
            color=color.yellow
        )
        
        # Update speed display
        def update_speed():
            # Calculate horizontal speed (ignoring vertical movement)
            horizontal_velocity = Vec2(self.player.velocity.x, self.player.velocity.z)
            speed = round(horizontal_velocity.length() * 50, 2)  # Scale for display
            multiplier = round(self.player.speed_multiplier, 2)
            self.speed_text.text = f"Speed: {speed} | Multiplier: {multiplier}x"
        
        self.update_speed = update_speed
    
    def create_environment(self):
        # Create ground plane
        ground = Entity(
            model='plane',
            scale=(100, 1, 100),
            color=color.gray,
            texture='white_cube',
            texture_scale=(100, 100),
            collider='box'
        )
        
        # Add some obstacles and landmarks to the environment
        for i in range(-5, 6, 2):
            for j in range(-5, 6, 2):
                if i == 0 and j == 0:
                    continue  # Skip center where player spawns
                
                # Create random colored blocks
                block_height = random.uniform(1, 3)
                Entity(
                    model='cube',
                    color=color.random_color(),
                    position=(i * 8, block_height/2, j * 8),
                    scale=(2, block_height, 2),
                    texture='white_cube',
                    collider='box'
                )
        
        # Create walls around the environment
        wall_height = 5
        wall_positions = [
            (0, wall_height/2, -50, 100, wall_height, 1),  # North wall
            (0, wall_height/2, 50, 100, wall_height, 1),   # South wall
            (-50, wall_height/2, 0, 1, wall_height, 100),  # West wall
            (50, wall_height/2, 0, 1, wall_height, 100),   # East wall
        ]
        
        for x, y, z, sx, sy, sz in wall_positions:
            Entity(
                model='cube',
                color=color.azure,
                position=(x, y, z),
                scale=(sx, sy, sz),
                collider='box'
            )
    
    def run(self):
        # Set up the update function
        def update():
            self.update_speed()
        
        # Register the update function
        self.app.update = update
        
        # Run the app
        self.app.run()


if __name__ == '__main__':
    game = Game()
    game.run() 