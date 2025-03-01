# 3D Bunnyhopping Game

A simple 3D first-person game with bunnyhopping mechanics built using the Ursina Engine.

![game](https://github.com/user-attachments/assets/c02b3de1-79e5-497e-a47e-92da3fcc0544)

## Requirements

- Python 3.7+
- Ursina Engine

## Installation

Install the required packages:

```bash
pip install ursina
```

## Running the Game

Simply run the main game file:

```bash
python bunny_hop_game.py
```

## Controls

- **W, A, S, D**: Move forward, left, backward, and right
- **Mouse**: Look around
- **Space**: Hold to bunnyhop continuously (you must be moving)

## Game Mechanics

Bunnyhopping is a movement technique where continuous jumping increases your movement speed. In this game:

1. Hold space bar while moving to perform bunny hops
2. Each consecutive jump increases your speed multiplier
3. Consecutive jumps receive a bigger speed boost than the first jump
4. The speed boost applies while moving in any direction
5. Your speed bonus decays if you stop jumping or stop moving
6. Speed decay slows down during long-distance travel for a smoother experience
7. There is no cap on maximum speed - how fast can you go?

The key to achieving maximum speed is to time your jumps perfectly - try to jump immediately after landing!

## Features

- First-person perspective
- Uncapped bunnyhopping mechanics with progressive speed boost
- Speed counter and multiplier display
- Distance traveled counter with color-coded milestones
- Procedurally generated infinite environment
- Various terrain types based on distance from origin
- Special landmarks at starting point for orientation

## Terrain Features

As you travel further from the starting point:
- Environment changes with different obstacle density
- You'll encounter specialized terrain types including:
  - Normal terrain with standard obstacles
  - Sparse areas with minimal obstacles
  - Dense areas with many obstacles
  - Ramp fields with elevated platforms and jumps
  - Platform fields with vertical challenges

## How to Play

1. Run the game
2. Use WASD to move and the mouse to look around
3. To bunnyhop, hold W (or any movement key) and **hold** the space bar
4. Try to jump in a rhythm, right after landing for the best speed boost
5. Try to achieve the highest speed possible!
6. See how far you can travel - watch the distance counter change colors at milestones!

## Customization

You can modify the following parameters in the code to adjust the bunnyhopping mechanics:

- `max_speed_multiplier`: Maximum speed multiplier (default: uncapped)
- `per_hop_multiplier_amount`: How much speed boost you get per hop (default: 0.25)
- `diminish_value`: Regular speed decay rate (default: 0.05)
- `long_distance_diminish`: Reduced decay rate for long-distance travel (default: 0.01)
- `jump_cooldown_max`: Time between jumps (default: 0.2) 
