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

def train_agent(agent_id, lock):
    import random
    import numpy as np
    random.seed()
    np.random.seed()

    # Initialize PyBoy instance for this agent
    pyboy = PyBoy(rom_path, sound=False, window="null")
    pyboy.set_emulation_speed(0)
    mario = pyboy.game_wrapper
    mario.game_area_mapping(mario.mapping_compressed, 0)
    mario.start_game()

    # Agent-specific variables
    alpha = 0.5             # Learning rate
    gamma = 0.9             # Discount factor
    epsilon = 1.0           # Exploration rate
    epsilon_min = 0.1
    epsilon_decay = 0.995

    step = 0
    episode = 0
    total_reward = 0

    previous_fitness = fitness_function(mario)
    state = get_state(mario)

    try:
        while True:
            step += 1
            # Choose an action (epsilon-greedy policy)
            if random.uniform(0, 1) < epsilon:
                # Exploration: random action
                action_index = random.randint(0, len(action_space) - 1)
            else:
                # Exploitation: choose the best known action
                with lock:
                    q_values = [Q_table.get((state, a), 0) for a in range(len(action_space))]
                max_q = max(q_values)
                max_actions = [i for i, q in enumerate(q_values) if q == max_q]
                action_index = random.choice(max_actions)

            action = action_space[action_index]

            # Press the selected buttons
            for btn in action:
                pyboy.button(btn)

            # Advance the game to see the effect of the action
            pyboy.tick(1 if args.mode == 'play' else 5)

            # Observe new state and reward
            next_state = get_state(mario)
            current_fitness = fitness_function(mario)
            reward = current_fitness - previous_fitness
            previous_fitness = current_fitness

            if args.mode == 'train':
                with lock:
                    # Update Q-table using the Q-learning formula
                    old_value = Q_table.get((state, action_index), 0)
                    next_max = max([Q_table.get((next_state, a), 0) for a in range(len(action_space))], default=0)
                    new_value = old_value + alpha * (reward + gamma * next_max - old_value)
                    Q_table[(state, action_index)] = new_value

            # Update state
            state = next_state

            # Decay epsilon
            if args.mode == 'train':
                epsilon = max(epsilon_min, epsilon * epsilon_decay)

            # Print current status
            if step % 1000 == 0:
                print(f"Agent {agent_id} - Step {step} - Level: {mario.world} - Level Progress: {mario.level_progress} - Fitness: {current_fitness:.2f} - Epsilon: {epsilon:.4f}")

            # Check for game over and reset if necessary
            if mario.lives_left < 0:
                # Reset the game
                mario.reset_game()
                state = get_state(mario)
                previous_fitness = fitness_function(mario)
    except Exception as e:
        print(f"Agent {agent_id} encountered an error: {e}")
    finally:
        pyboy.stop()

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
