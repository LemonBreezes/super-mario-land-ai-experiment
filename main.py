#!/usr/bin/env python3
import argparse

from pyboy import PyBoy
import random
import numpy as np
random.seed()
np.random.seed()
import pickle
import signal
import multiprocessing
from multiprocessing import Manager

parser = argparse.ArgumentParser(description='Super Mario Land AI')
parser.add_argument('--mode', choices=['train', 'play'], default='train', help='Mode to run the script: train or play')
args = parser.parse_args()


# Initialize PyBoy with the selected ROM
manager = Manager()
Q_table = manager.dict()
alpha = 0.1             # Learning rate
gamma = 0.9             # Discount factor
epsilon = 0.1           # Exploration rate (for epsilon-greedy policy)
epsilon_min = 0.01      # Minimum exploration rate
epsilon_decay = 0.995   # Decay rate for epsilon

if args.mode == 'play':
    epsilon = 0           # Disable exploration in play mode
    epsilon_min = 0
    epsilon_decay = 1     # No decay
rom_path = 'roms/Super Mario Land (World) (Rev A).gb'
if not rom_path:
    exit()

if args.mode == 'play':
    pyboy = PyBoy(rom_path, sound=False, window="SDL2")
    pyboy.set_emulation_speed(1)  # Normal speed
else:
    pyboy = PyBoy(rom_path, sound=False, window="null")
    pyboy.set_emulation_speed(0)  # Maximum speed

mario = pyboy.game_wrapper
assert pyboy.cartridge_title == "SUPER MARIOLAN"
mario.game_area_mapping(mario.mapping_compressed, 0)
mario.start_game()

assert mario.score == 0
assert mario.lives_left == 2
assert mario.time_left == 400
assert mario.world == (1, 1)
last_time = mario.time_left

# print(mario)
# Output:
# Super Mario Land: World 1-1
# Coins: 0
# lives_left: 2
# Score: 0
# Time left: 400
# Level progress: 251
# Sprites on screen:
# Sprite [3]: Position: (35, 112), Shape: (8, 8), Tiles: (Tile: 0), On screen: True
# Sprite [4]: Position: (43, 112), Shape: (8, 8), Tiles: (Tile: 1), On screen: True
# Sprite [5]: Position: (35, 120), Shape: (8, 8), Tiles: (Tile: 16), On screen: True
# Sprite [6]: Position: (43, 120), Shape: (8, 8), Tiles: (Tile: 17), On screen: True
# Tiles on screen:
#        0   1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17  18  19
# ____________________________________________________________________________________
# 0  |   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0
# 1  |   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0
# 2  |   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0
# 3  |   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0
# 4  |   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0
# 5  |   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0
# 6  |   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0
# 7  |   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0
# 8  |   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0
# 9  |   0   0   0   0   0  13   0   0   0   0   0   0   0   0   0   0   0   0   0   0
# 10 |   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0
# 11 |   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0
# 12 |   0  14  14   0   1   1   0   0   0   0   0   0   0   0   0   0   0   0   0   0
# 13 |   0  14  14   0   1   1   0   0   0   0   0   0   0   0   0   0   0   0   0   0
# 14 |  10  10  10  10  10  10  10  10  10  10  10  10  10  10  10  10  10  10  10  10
# 15 |  10  10  10  10  10  10  10  10  10  10  10  10  10  10  10  10  10  10  10  10

action_space = [
    [],                          # No action
    ['right'],                   # Move right
    ['a'],                       # Jump
    ['right', 'a'],              # Move right and jump
    ['right', 'b'],              # Run right
    ['right', 'b', 'a'],         # Run right and jump
]

def get_state(mario):
    # Simplify the state to reduce the state space
    state = (
        int(mario.level_progress / 10),   # Discretize level progress
        mario.lives_left,
        mario.world[0],                   # World number
        mario.world[1],                   # Level number
    )
    return state

def fitness_function(mario):
    return (
        mario.level_progress * 10 +  # Prioritize level progress
        (400 - mario.time_left) * (-10) +  # Reward for using less time (speedrun)
        mario.world[0] * 10000 +  # Large bonus for completing worlds
        mario.world[1] * 1000 +   # Large bonus for completing levels
        mario.lives_left * 100 +  # Small bonus for remaining lives
        mario.score / 100  # Small bonus for score (might include coin collection speed)
    )

if __name__ == "__main__":
    num_processes = multiprocessing.cpu_count()
    processes = []
    lock = manager.Lock()

    for i in range(num_processes):
        p = multiprocessing.Process(target=train_agent, args=(i, lock))
        processes.append(p)
        p.start()

    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("Interrupted by user. Terminating processes...")
        for p in processes:
            p.terminate()
        for p in processes:
            p.join()

    if args.mode == 'train':
        with open('q_table.pkl', 'wb') as f:
            pickle.dump(dict(Q_table), f)
