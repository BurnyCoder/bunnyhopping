from ursina import *
import random
import math


class Environment:
    def __init__(self, player):
        self.player = player
        
        # Environment generation parameters
        self.chunk_size = 40  # Size of each terrain chunk
        self.render_distance = 4  # Chunks to render around player
        self.chunks = {}  # Store all generated chunks
        
        # Create initial environment
        self.create_base_ground()
        self.generate_chunks_around_player()
        
        # Create updater entity for terrain generation
        self.terrain_generator = Entity()
        self.terrain_generator.update = self.update_terrain
        
        # Store player's initial position for distance calculation
        self.initial_player_position = Vec3(self.player.position)
        
        # Debug timing
        self.last_debug_time = time.time()
    
    def create_base_ground(self):
        """Create the main ground plane and starting area landmarks."""
        # Main ground that follows the player
        self.main_ground = Entity(
            model='plane',
            scale=(1000, 1, 1000),
            color=color.rgb(50, 50, 60),  # Dark blue-gray monolithic color
            collider='box'
        )
        
        # Ground updater entity
        self.ground_updater = Entity()
        self.ground_updater.update = self.update_ground
        
        # Create starting area landmarks
        # Center marker
        Entity(
            model='sphere',
            scale=3,
            y=1.5,
            color=color.cyan,
            texture='white_cube'
        )
        
        # Circle of pillars
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
        """Update the main ground position to follow the player."""
        self.main_ground.position = Vec3(
            self.player.position.x,
            0,
            self.player.position.z
        )
    
    def update_terrain(self):
        """Update terrain generation based on player position."""
        # Get player's current chunk coordinates
        player_chunk_x = int(self.player.position.x // self.chunk_size)
        player_chunk_z = int(self.player.position.z // self.chunk_size)
        
        # Generate new chunks and remove distant ones
        self.generate_chunks_around_player()
        self.remove_distant_chunks(player_chunk_x, player_chunk_z)
        
        # Debug display every 5 seconds
        if time.time() - self.last_debug_time > 5:
            distance = Vec2(self.player.position.x, self.player.position.z).length()
            print(f"Current position: {self.player.position}, Distance: {distance:.1f}m, Chunks: {len(self.chunks)}")
            self.last_debug_time = time.time()
    
    def generate_chunks_around_player(self):
        """Generate terrain chunks around the player's current position."""
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
        """Generate a single terrain chunk with obstacles and features."""
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
        """Remove chunks that are outside the render distance."""
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
    
    def get_distance_from_start(self):
        """Calculate horizontal distance from start position."""
        start_pos_2d = Vec2(self.initial_player_position.x, self.initial_player_position.z)
        current_pos_2d = Vec2(self.player.position.x, self.player.position.z)
        return (current_pos_2d - start_pos_2d).length() 