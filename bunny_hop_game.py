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
        self.jump_upwards_speed = 0.2
        self.speed_multiplier = 1.0
        self.max_speed_multiplier = 2.5
        self.per_hop_multiplier_amount = 0.15
        self.diminish_value = 0.05
        self.is_jumping = False
        self.jump_time = 0
        self.max_jump_time = 0.5
        self.jump_cooldown = 0
        self.jump_cooldown_max = 0.1
        
        # For calculating speed display
        self.last_position = Vec3(self.position)
        self.velocity = Vec3(0, 0, 0)

    def update(self):
        # Calculate velocity for display
        self.velocity = self.position - self.last_position
        self.last_position = Vec3(self.position.x, self.position.y, self.position.z)
        
        # Handle bunnyhopping
        if held_keys['space']:
            if self.grounded and self.jump_cooldown <= 0:
                # Start a new jump from the ground
                self.is_jumping = True
                self.jump_time = 0
                self.jump_cooldown = self.jump_cooldown_max
                
                # Increase speed multiplier for each jump
                self.speed_multiplier = min(self.max_speed_multiplier, 
                                           self.speed_multiplier + self.per_hop_multiplier_amount)
            
            if self.is_jumping:
                self.jump_time += time.dt
                
                # Apply upward movement during jump
                self.y += self.jump_upwards_speed
                
                # Apply forward movement with boosted speed
                move_direction = self.get_movement_direction()
                if move_direction.length() > 0:
                    # Apply directional movement with speed boost
                    self.position += move_direction * self.original_speed * self.speed_multiplier * time.dt
                
                # End jump after max time
                if self.jump_time >= self.max_jump_time:
                    self.is_jumping = False
        else:
            # Not holding space
            self.is_jumping = False
            
        # Decrease jump cooldown
        if self.jump_cooldown > 0:
            self.jump_cooldown -= time.dt
            
        # Gradually decrease speed multiplier when not jumping or not moving
        if (not self.is_jumping or not any(held_keys[key] for key in ['w', 'a', 's', 'd'])) and self.speed_multiplier > 1.0:
            self.speed_multiplier = max(1.0, self.speed_multiplier - self.diminish_value * time.dt)
        
        # Only use the parent class update if not bunnyhopping
        if not self.is_jumping:
            super().update()
    
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
    
    def input(self, key):
        # Only pass input to parent if not currently bunnyhopping
        if not self.is_jumping:
            super().input(key)


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