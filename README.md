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

## Customization

You can modify the following parameters in the code to adjust the bunnyhopping mechanics:

- `max_speed_multiplier`: Maximum speed multiplier (default: uncapped)
- `per_hop_multiplier_amount`: How much speed boost you get per hop (default: 0.25)
- `diminish_value`: Regular speed decay rate (default: 0.05)
- `long_distance_diminish`: Reduced decay rate for long-distance travel (default: 0.01)
- `jump_cooldown_max`: Time between jumps (default: 0.2) 
