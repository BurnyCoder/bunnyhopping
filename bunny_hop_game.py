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


class Game:
    def __init__(self):
        # Initialize the Ursina app
        self.app = Ursina()
        
        # Basic scene setup
        window.title = "Bunnyhop 3D"
        window.borderless = False
        window.exit_button.visible = False
        window.fps_counter.enabled = True
        
        # Fog is now disabled
        # scene.fog_color = color.rgb(150, 170, 200)
        # scene.fog_density = 0.01
        
        # Create initial ground only
        self.create_base_ground()
        
        # Add player with bunnyhop controller
        self.player = BunnyHopController(
            position=Vec3(0, 2, 0),
            collider='box',
            speed=8
        )
        
        # Set initial player position for distance tracking
        self.initial_player_position = Vec3(self.player.position)
        
        # Now create the procedural environment around the player
        self.create_procedural_environment()
        
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
        
        # Distance traveled display
        self.distance_text = Text(
            text="Distance: 0 meters",
            origin=(0, 0),
            position=(0, 0.3),
            color=color.white
        )
        
        # Create an entity to handle updates
        self.ui_updater = Entity()
        self.ui_updater.update = self.update_ui
    
    def update_ui(self):
        # Update speed
        self.update_speed()
        
        # Update distance traveled
        self.update_distance()
    
    def update_distance(self):
        # Calculate distance from starting point (ignoring Y for better measurement)
        start_pos_2d = Vec2(self.initial_player_position.x, self.initial_player_position.z)
        current_pos_2d = Vec2(self.player.position.x, self.player.position.z)
        distance = (current_pos_2d - start_pos_2d).length()
        
        # Round for display
        distance_meters = round(distance, 1)
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

    def create_base_ground(self):
        # Instead of a single large ground, create a ground that follows the player
        self.main_ground = Entity(
            model='plane',
            scale=(1000, 1, 1000),
            color=color.rgb(50, 50, 60),  # Dark blue-gray monolithic color
            # Removed texture for a solid color appearance
            collider='box'
        )
        
        # Create a ground update entity
        self.ground_updater = Entity()
        self.ground_updater.update = self.update_ground
        
        # Add some landmarks at the origin to mark the starting point
        Entity(
            model='sphere',
            scale=3,
            y=1.5,
            color=color.cyan,
            texture='white_cube'
        )
        
        # Add a circle of pillars around the starting point
        for i in range(8):
            angle = i * math.pi / 4
            x = math.cos(angle) * 15
            z = math.sin(angle) * 15
            Entity(
                model='cube',
                position=(x, 2.5, z),
                scale=(1, 5, 1),
                color=color.light_gray,
                texture='white_cube',
                collider='box'
            )
    
    def update_ground(self):
        # Update the main ground position to follow the player
        # Only update X and Z, keep Y at 0
        self.main_ground.position = Vec3(
            self.player.position.x,
            0,
            self.player.position.z
        )
    
    def create_procedural_environment(self):
        # Remove the boundary walls to allow infinite movement
        
        # Store all generated chunks
        self.chunks = {}
        self.chunk_size = 40  # Size of each terrain chunk
        self.render_distance = 4  # Increased render distance (was 3)
        
        # Create initial chunks around the player
        self.generate_chunks_around_player()
        
        # Add terrain generation system to follow the player
        self.terrain_generator = Entity()
        self.terrain_generator.update = self.update_terrain
    
    def update_terrain(self):
        # Get player's current chunk coordinates
        player_chunk_x = int(self.player.position.x // self.chunk_size)
        player_chunk_z = int(self.player.position.z // self.chunk_size)
        
        # Generate or destroy chunks based on distance from player
        self.generate_chunks_around_player()
        self.remove_distant_chunks(player_chunk_x, player_chunk_z)
        
        # Debug display in console every 5 seconds
        if not hasattr(self, 'last_debug_time'):
            self.last_debug_time = time.time()
        
        if time.time() - self.last_debug_time > 5:
            distance = Vec2(self.player.position.x, self.player.position.z).length()
            print(f"Current position: {self.player.position}, Distance: {distance:.1f}m, Chunks: {len(self.chunks)}")
            self.last_debug_time = time.time()
    
    def generate_chunks_around_player(self):
        # Get player's current chunk coordinates
        player_chunk_x = int(self.player.position.x // self.chunk_size)
        player_chunk_z = int(self.player.position.z // self.chunk_size)
        
        # Generate chunks in render distance
        for x in range(player_chunk_x - self.render_distance, player_chunk_x + self.render_distance + 1):
            for z in range(player_chunk_z - self.render_distance, player_chunk_z + self.render_distance + 1):
                chunk_key = f"{x}_{z}"
                
                # Only generate if the chunk doesn't exist
                if chunk_key not in self.chunks:
                    self.generate_chunk(x, z, chunk_key)
    
    def generate_chunk(self, chunk_x, chunk_z, chunk_key):
        # Calculate world position of chunk
        world_x = chunk_x * self.chunk_size
        world_z = chunk_z * self.chunk_size
        
        # Create a parent entity for all objects in this chunk
        chunk_parent = Entity(position=(0, 0, 0))
        self.chunks[chunk_key] = chunk_parent
        
        # Calculate distance from origin for variety
        distance_from_origin = math.sqrt(chunk_x**2 + chunk_z**2)
        
        # Generate random obstacles in the chunk
        num_obstacles = random.randint(3, 8)  # Random number of obstacles per chunk
        
        # Add terrain variety based on distance
        terrain_type = 'normal'
        if distance_from_origin > 10:
            # Far chunks have special terrain types
            terrain_type = random.choice(['normal', 'sparse', 'dense', 'ramp_field', 'platform_field'])
        
        # Create different terrain types
        if terrain_type == 'sparse':
            num_obstacles = random.randint(1, 3)
        elif terrain_type == 'dense':
            num_obstacles = random.randint(8, 15)
        elif terrain_type == 'ramp_field':
            num_obstacles = random.randint(5, 10)
            # Higher chance of ramps
            ramp_chance = 0.7
        elif terrain_type == 'platform_field':
            num_obstacles = random.randint(5, 10)
            # Higher chance of platforms
            platform_chance = 0.7
        else:
            # Normal terrain with standard obstacle distribution
            ramp_chance = 0.3
            platform_chance = 0.3
        
        for _ in range(num_obstacles):
            # Random position within the chunk
            local_x = random.uniform(0, self.chunk_size)
            local_z = random.uniform(0, self.chunk_size)
            
            # Create obstacle
            block_height = random.uniform(1, 5)  # Varying heights
            
            # Avoid placing obstacles too close to the player's starting position
            if (chunk_x == 0 and chunk_z == 0 and 
                abs(local_x) < 10 and abs(local_z) < 10):
                continue
                
            # Create the block with a random color
            block_color = color.random_color()
            if distance_from_origin > 5:
                # Add some theme colors based on distance
                hue = (distance_from_origin * 0.05) % 1.0
                block_color = color.hsv(hue, 0.7, 0.8)
                
            Entity(
                model='cube',
                color=block_color,
                position=(world_x + local_x, block_height/2, world_z + local_z),
                scale=(random.uniform(2, 4), block_height, random.uniform(2, 4)),
                texture='white_cube',
                collider='box',
                parent=chunk_parent
            )
            
            # Occasionally add a ramp or special structure
            if random.random() < (ramp_chance if 'ramp_chance' in locals() else 0.3):
                ramp_type = random.choice(['ramp', 'platform', 'arch'])
                
                if terrain_type == 'ramp_field':
                    ramp_type = 'ramp'
                elif terrain_type == 'platform_field':
                    ramp_type = 'platform'
                
                if ramp_type == 'ramp':
                    # Create a ramp
                    ramp_height = random.uniform(2, 4)
                    ramp_length = random.uniform(4, 8)
                    
                    Entity(
                        model='cube',
                        color=color.orange,
                        position=(world_x + local_x + ramp_length/2, ramp_height/2, world_z + local_z + 5),
                        scale=(ramp_length, ramp_height, 3),
                        rotation=(0, 0, -15),  # Tilted to create a ramp
                        texture='white_cube',
                        collider='box',
                        parent=chunk_parent
                    )
                    
                elif ramp_type == 'platform':
                    # Create a platform
                    platform_height = random.uniform(2, 6)
                    
                    Entity(
                        model='cube',
                        color=color.azure,
                        position=(world_x + local_x, platform_height, world_z + local_z + 5),
                        scale=(4, 1, 4),
                        texture='white_cube',
                        collider='box',
                        parent=chunk_parent
                    )
                    
                elif ramp_type == 'arch':
                    # Create an arch
                    arch_height = random.uniform(4, 6)
                    
                    # Left pillar
                    Entity(
                        model='cube',
                        color=color.violet,
                        position=(world_x + local_x - 3, arch_height/2, world_z + local_z + 5),
                        scale=(1, arch_height, 1),
                        texture='white_cube',
                        collider='box',
                        parent=chunk_parent
                    )
                    
                    # Right pillar
                    Entity(
                        model='cube',
                        color=color.violet,
                        position=(world_x + local_x + 3, arch_height/2, world_z + local_z + 5),
                        scale=(1, arch_height, 1),
                        texture='white_cube',
                        collider='box',
                        parent=chunk_parent
                    )
                    
                    # Top
                    Entity(
                        model='cube',
                        color=color.violet,
                        position=(world_x + local_x, arch_height, world_z + local_z + 5),
                        scale=(7, 1, 1),
                        texture='white_cube',
                        collider='box',
                        parent=chunk_parent
                    )
    
    def remove_distant_chunks(self, player_chunk_x, player_chunk_z):
        # Remove chunks that are too far from the player
        chunks_to_remove = []
        
        for chunk_key in self.chunks:
            x, z = map(int, chunk_key.split('_'))
            
            # Check if chunk is outside render distance
            if (abs(x - player_chunk_x) > self.render_distance + 1 or 
                abs(z - player_chunk_z) > self.render_distance + 1):
                chunks_to_remove.append(chunk_key)
        
        # Destroy the chunks that are too far
        for chunk_key in chunks_to_remove:
            if chunk_key in self.chunks:
                destroy(self.chunks[chunk_key])
                del self.chunks[chunk_key]
    
    def update_speed(self):
        # Calculate horizontal speed (ignoring vertical movement)
        horizontal_velocity = Vec2(self.player.velocity.x, self.player.velocity.z)
        
        # Calculate speed - use a better scaling factor based on the original player speed
        speed_factor = 50 / self.player.original_speed  # Normalize to make display more intuitive
        raw_speed = horizontal_velocity.length() * speed_factor
        
        # Apply some smoothing for better display
        if hasattr(self, 'displayed_speed'):
            # Smooth transition between speed values (lerp)
            self.displayed_speed = lerp(self.displayed_speed, raw_speed, time.dt * 5)
        else:
            self.displayed_speed = raw_speed
            
        # Round for display
        speed = round(self.displayed_speed, 1)
        multiplier = round(self.player.speed_multiplier, 2)
        
        # Set color based on multiplier (green to yellow to red as speed increases)
        # Now with adjusted ranges for the uncapped multiplier
        capped_multiplier = min(10.0, self.player.speed_multiplier)  # Cap color changes at 10x
        normalized_multiplier = (capped_multiplier - 1.0) / 9.0  # Range 1.0 to 10.0 maps to 0.0 to 1.0
        
        speed_color = color.rgb(
            255 * min(1, normalized_multiplier * 2),  # Red increases faster
            255 * max(0, 1 - normalized_multiplier),  # Green decreases as we go faster
            0  # No blue
        )
        
        # Update the text
        self.speed_text.text = f"Speed: {speed} | Multiplier: {multiplier}x"
        self.speed_text.color = speed_color
    
    def run(self):
        # Run the app
        self.app.run()


if __name__ == '__main__':
    game = Game()
    game.run() 