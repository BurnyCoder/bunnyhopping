#!/usr/bin/env python3
"""
Simple 3D First-Person Game using Ursina Engine.
WASD to move, Space to jump, mouse to look around.
Collect the rotating yellow cubes to increase your score!
"""
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController


def main():
    # Initialize the game
    app = Ursina()
    
    # Basic setup
    window.title = "Simple 3D FPS Game"
    window.borderless = False
    window.fullscreen = False
    window.exit_button.visible = True
    window.fps_counter.enabled = True

    # Global variables
    score = 0
    collectibles = []
    
    # Score text
    score_text = Text(
        text=f"Score: {score}",
        position=(-0.85, 0.45),
        scale=2,
        color=color.yellow
    )
    
    # Instruction text
    instructions = Text(
        text="Use WASD to move, SPACE to jump, and mouse to look around.\nCollect yellow cubes to increase your score!",
        position=(-0.5, 0.35),
        scale=1.5,
        color=color.black
    )

    # Create a ground
    ground = Entity(
        model="plane",
        scale=(20, 1, 20),
        color=color.green,
        texture="white_cube",
        texture_scale=(20, 20),
        collider="box"
    )
    
    # Create some obstacles and walls
    for i in range(10):
        box = Entity(
            model="cube",
            color=color.random_color(),
            position=(random.uniform(-9, 9), 0.5, random.uniform(-9, 9)),
            scale=(random.uniform(0.5, 2), random.uniform(0.5, 3), random.uniform(0.5, 2)),
            collider="box"
        )
    
    # Add some walls to define boundaries
    wall_1 = Entity(model="cube", scale=(20, 3, 1), position=(0, 1.5, 10), color=color.azure, collider="box")
    wall_2 = Entity(model="cube", scale=(20, 3, 1), position=(0, 1.5, -10), color=color.azure, collider="box")
    wall_3 = Entity(model="cube", scale=(1, 3, 20), position=(10, 1.5, 0), color=color.azure, collider="box")
    wall_4 = Entity(model="cube", scale=(1, 3, 20), position=(-10, 1.5, 0), color=color.azure, collider="box")
    
    # Add a skybox
    Sky()
    
    # Add player controller
    player = FirstPersonController(
        position=(0, 1, 0),
        speed=5,
        mouse_sensitivity=Vec2(40, 40),
        jump_height=2
    )
    
    # Light
    DirectionalLight(y=2, z=3, rotation=(45, 45, 45))
    
    # Collectible class
    class Collectible(Entity):
        def __init__(self, position):
            super().__init__(
                model="cube",
                color=color.yellow,
                scale=0.5,
                position=position,
                collider="box"
            )
            self.rotation_speed = Vec3(random.uniform(1, 5), random.uniform(1, 5), random.uniform(1, 5))
            self.collected = False
            collectibles.append(self)
            
        def update(self):
            # Rotate the collectible
            self.rotation += self.rotation_speed * time.dt
            
            # Check for collision with player
            if not self.collected and distance(self.position, player.position) < 1.5:
                self.collect()
        
        def collect(self):
            nonlocal score
            score += 1
            score_text.text = f"Score: {score}"
            self.collected = True
            destroy(self, delay=0.1)
            collectibles.remove(self)
            # Create a new collectible
            spawn_collectible()
    
    # Spawn a collectible at a random position
    def spawn_collectible():
        x = random.uniform(-9, 9)
        z = random.uniform(-9, 9)
        # Make sure collectibles don't spawn inside obstacles
        y = 0.5  # Slightly above ground
        Collectible(position=(x, y, z))
    
    # Spawn initial collectibles
    for _ in range(5):
        spawn_collectible()
    
    # Update function
    def update():
        # Exit on escape key
        if held_keys['escape']:
            application.quit()
    
    # Run the game
    app.run()


if __name__ == "__main__":
    main() 