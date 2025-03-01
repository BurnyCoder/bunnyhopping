# 3D Bunnyhopping Game

A simple 3D first-person game with bunnyhopping mechanics built using the Ursina Engine.

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

Bunnyhopping is a movement technique where continuous jumping increases your movement speed. By holding space while moving, your character will automatically jump repeatedly, and each jump increases your speed multiplier. The speed boost decays if you stop jumping or stop moving.

## Features

- First-person perspective
- Bunnyhopping mechanics with speed boost
- Speed counter and multiplier display
- Simple 3D environment with obstacles

## How to Play

1. Run the game
2. Use WASD to move and the mouse to look around
3. To bunnyhop, hold W (or any movement key) and **hold** the space bar
4. Try to achieve the highest speed possible!

## Customization

You can modify the following parameters in the code to adjust the bunnyhopping mechanics:

- `max_speed_multiplier`: Maximum speed multiplier (default: 2.5)
- `per_hop_multiplier_amount`: How much speed boost you get per hop (default: 0.15)
- `diminish_value`: How quickly speed decays (default: 0.05)
- `jump_upwards_speed`: How high each jump goes (default: 0.2)
- `max_jump_time`: Maximum duration of a jump (default: 0.5)
- `jump_cooldown_max`: Time between jumps (default: 0.1) 