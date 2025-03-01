"""
Game objects for the 3D game.
"""
from ursina import *
import random
import math


class Collectible(Entity):
    """A collectible item that rotates and can be picked up."""
    
    def __init__(self, position, **kwargs):
        super().__init__(
            model='sphere',
            scale=0.5,
            color=color.gold,
            position=position,
            collider='sphere',
            **kwargs
        )
        self.rotation_speed = random.uniform(50, 100)
        
    def update(self):
        """Update the collectible (rotation)."""
        self.rotation_y += self.rotation_speed * time.dt


class Goal(Entity):
    """The goal to reach at the end of the game."""
    
    def __init__(self, position, **kwargs):
        super().__init__(
            model='cube',
            scale=(2, 3, 2),
            color=color.azure,
            position=position,
            collider='box',
            **kwargs
        )
        # Add pulsing effect
        self.original_scale = self.scale
        self.pulse_speed = 1
        
    def update(self):
        """Update the goal (pulsing effect)."""
        pulse = math.sin(time.time() * self.pulse_speed) * 0.1 + 1
        self.scale = self.original_scale * pulse 