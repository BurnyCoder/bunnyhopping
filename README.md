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

Bunnyhopping is a movement technique where continuous jumping increases your movement speed. In this game:

1. Hold space bar while moving to perform bunny hops
2. Each consecutive jump increases your speed multiplier
3. Consecutive jumps receive a bigger speed boost than the first jump
4. The speed boost applies while moving in any direction
5. Your speed bonus decays if you stop jumping or stop moving

The key to achieving maximum speed is to time your jumps perfectly - try to jump immediately after landing!

## Features

- First-person perspective
- Bunnyhopping mechanics with progressive speed boost
- Speed counter and multiplier display
- Simple 3D environment with obstacles

## How to Play

1. Run the game
2. Use WASD to move and the mouse to look around
3. To bunnyhop, hold W (or any movement key) and **hold** the space bar
4. Try to jump in a rhythm, right after landing for the best speed boost
5. Try to achieve the highest speed possible!

## Customization

You can modify the following parameters in the code to adjust the bunnyhopping mechanics:

- `max_speed_multiplier`: Maximum speed multiplier (default: 3.0)
- `per_hop_multiplier_amount`: How much speed boost you get per hop (default: 0.25)
- `diminish_value`: How quickly speed decays (default: 0.05)
- `jump_cooldown_max`: Time between jumps (default: 0.2) 