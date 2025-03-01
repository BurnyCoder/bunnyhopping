#!/usr/bin/env python3
"""
A simple 3D first-person game created with Ursina.
"""
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import math
from game_objects import Collectible, Goal


class Game:
    """Main game class."""
    
    def __init__(self):
        # Initialize the Ursina app
        self.app = Ursina()
        
        # Set up the window
        window.title = "Simple 3D Game"
        window.borderless = False
        window.fullscreen = False
        window.exit_button.visible = False
        window.fps_counter.enabled = True
        
        # Create the environment
        self.create_environment()
        
        # Create the player
        self.player = FirstPersonController(
            position=(0, 1, 0),
            speed=5
        )
        
        # Create collectibles and goal
        self.collectibles = []
        self.create_collectibles(8)
        self.create_goal()
        
        # Set up UI
        self.score = 0
        self.score_text = Text(
            text=f"Score: {self.score} / {len(self.collectibles)}", 
            position=(-0.85, 0.45),
            scale=2
        )
        self.message_text = Text(
            text="Collect all items and reach the goal!",
            position=(0, 0.3),
            origin=(0, 0),
            scale=2
        )
        invoke(setattr, self.message_text, 'enabled', False, delay=3)
        
        # Game state
        self.game_over = False
        
        # Check for collisions with collectibles and goal
        self.check_collisions()


    def create_environment(self):
        """Create the 3D environment."""
        # Create a ground plane
        ground = Entity(
            model='plane',
            scale=(20, 1, 20),
            color=color.green,
            texture='white_cube',
            texture_scale=(20, 20),
            collider='box'
        )
        
        # Create some walls
        wall_positions = [
            (0, 1, 10),   # North
            (0, 1, -10),  # South
            (10, 1, 0),   # East
            (-10, 1, 0),  # West
        ]
        
        wall_rotations = [
            (0, 0, 0),
            (0, 180, 0),
            (0, 90, 0),
            (0, 270, 0),
        ]
        
        for pos, rot in zip(wall_positions, wall_rotations):
            wall = Entity(
                model='cube',
                scale=(20, 2, 0.5),
                position=pos,
                rotation=rot,
                color=color.light_gray,
                texture='white_cube',
                texture_scale=(10, 2),
                collider='box'
            )
        
        # Add some random cubes as obstacles
        for i in range(10):
            cube = Entity(
                model='cube',
                color=color.random_color(),
                position=(
                    random.uniform(-8, 8),
                    0.5,
                    random.uniform(-8, 8)
                ),
                scale=(1, 1, 1),
                collider='box'
            )
            
        # Add a light source
        DirectionalLight(
            color=color.white,
            direction=(0.5, -0.8, 0.5),
            shadows=True
        )
        
        # Add skybox
        Sky()
    
    
    def create_collectibles(self, count):
        """Create collectible items."""
        for i in range(count):
            # Make sure collectibles don't spawn too close to the player
            while True:
                pos = (
                    random.uniform(-9, 9),
                    1,
                    random.uniform(-9, 9)
                )
                # Check if position is far enough from player start position
                # Calculate distance manually instead of using .distance method
                player_pos = Vec3(0, 1, 0)
                pos_vec = Vec3(*pos)
                dist = (pos_vec - player_pos).length()
                if dist > 3:
                    break
            
            collectible = Collectible(position=pos)
            self.collectibles.append(collectible)
    
    
    def create_goal(self):
        """Create the goal."""
        # Place goal at a random position along the perimeter
        side = random.choice(['north', 'south', 'east', 'west'])
        if side == 'north':
            pos = (random.uniform(-8, 8), 1.5, 8)
        elif side == 'south':
            pos = (random.uniform(-8, 8), 1.5, -8)
        elif side == 'east':
            pos = (8, 1.5, random.uniform(-8, 8))
        else:  # west
            pos = (-8, 1.5, random.uniform(-8, 8))
        
        self.goal = Goal(position=pos)
    
    
    def check_collisions(self):
        """Check for collisions with collectibles and goal."""
        def update():
            hit_info = self.player.intersects()
            if hit_info.hit:
                # Check if hit a collectible
                for collectible in self.collectibles[:]:
                    if hit_info.entity == collectible:
                        self.collect_item(collectible)
                
                # Check if hit the goal and all collectibles are collected
                if hit_info.entity == self.goal and self.score == len(self.collectibles):
                    self.win_game()
        
        self.update_task = taskMgr.add(lambda task: update() or task.cont)
    
    
    def collect_item(self, collectible):
        """Collect an item and update score."""
        if collectible in self.collectibles:
            collectible.disable()
            self.score += 1
            self.score_text.text = f"Score: {self.score} / {len(self.collectibles)}"
            # Play sound effect
            Audio('click', autoplay=True)
            
            # Show message if all items collected
            if self.score == len(self.collectibles):
                self.message_text.text = "All items collected! Go to the goal!"
                self.message_text.enabled = True
                invoke(setattr, self.message_text, 'enabled', False, delay=3)
    
    
    def win_game(self):
        """Win the game."""
        if not self.game_over:
            self.game_over = True
            self.player.disable()
            
            # Show win message
            win_text = Text(
                text="You Win!",
                origin=(0, 0),
                scale=5,
                color=color.green
            )
            
            # Play win sound
            Audio('coin', autoplay=True)
            
            # Add restart button
            Button(
                text="Play Again",
                scale=(0.2, 0.1),
                position=(0, -0.1),
                on_click=self.restart_game
            )
            
            # Add quit button
            Button(
                text="Quit",
                scale=(0.2, 0.1),
                position=(0, -0.25),
                on_click=application.quit
            )
    
    
    def restart_game(self):
        """Restart the game."""
        application.restart()
    
    
    def run(self):
        """Run the game."""
        self.app.run()


def main():
    """Run the game."""
    game = Game()
    game.run()


if __name__ == '__main__':
    main() 