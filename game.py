from ursina import *
from controllers.bunny_hop_controller import BunnyHopController
from world.environment import Environment
from ui.hud import HUD


class Game:
    def __init__(self):
        # Initialize the Ursina app
        self.app = Ursina()
        
        # Basic scene setup
        self.setup_window()
        
        # Add player with bunnyhop controller
        self.player = BunnyHopController(
            position=Vec3(0, 2, 0),
            collider='box',
            speed=8
        )
        
        # Create environment
        self.environment = Environment(self.player)
        
        # Create HUD
        self.hud = HUD(self.player, self.environment)
    
    def setup_window(self):
        """Configure the game window and settings."""
        window.title = "Bunnyhop 3D"
        window.borderless = False
        window.exit_button.visible = False
        window.fps_counter.enabled = True
    
    def run(self):
        """Run the game."""
        self.app.run()
