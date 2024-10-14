#!/usr/bin/env python3
import argparse

from pyboy import PyBoy
import random
import numpy as np
random.seed()
np.random.seed()
import pickle
import signal

parser = argparse.ArgumentParser(description='Super Mario Land AI')
parser.add_argument('--mode', choices=['train', 'play'], default='train', help='Mode to run the script: train or play')
args = parser.parse_args()

def signal_handler(sig, frame):
    print("Emulation interrupted by user.")
    if args.mode == 'train':
        with open('q_table.pkl', 'wb') as f:
            pickle.dump(Q_table, f)
    pyboy.stop()
    exit(0)

# Initialize PyBoy with the selected ROM
Q_table = {}
try:
    signal.signal(signal.SIGINT, signal_handler)
    with open('q_table.pkl', 'rb') as f:
        Q_table = pickle.load(f)
except FileNotFoundError:
    if args.mode == 'play':
        print("No trained Q-table found. Please train the model before playing.")
        exit()
    else:
        Q_table = {}
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

action_space = [
    # [],                          # No action
    ['right'],                   # Move right
    # ['a'],                       # Jump
    ['right', 'a'],              # Move right and jump
    ['right', 'b'],              # Run right
    ['right', 'b', 'a'],         # Run right and jump
]

def get_state(mario):
    # Simplify the state to reduce the state space
    state = (
        int(mario.level_progress / 10),   # Discretize level progress
        mario.world[0],                   # World number
        mario.world[1],                   # Level number
    )
    return state

def fitness_function(mario):
    return (
        mario.level_progress * 10 +  # Prioritize level progress
        (400 - mario.time_left) * (-1) +  # Reward for using less time (speedrun)
        mario.world[0] * 10000 +  # Large bonus for completing worlds
        mario.world[1] * 2000 +   # Large bonus for completing levels
        mario.lives_left * 100 +  # Small bonus for remaining lives
        mario.coins * 2 +        # Small bonus for coin collectionn
        mario.score / 100  # Small bonus for score (might include coin collection speed)
    )

# Main emulation loop
step = 0
try:
    # Initialize state
    state = get_state(mario)
    previous_fitness = fitness_function(mario)

    while True:
        step += 1
        # Choose an action (epsilon-greedy policy)
        if random.uniform(0, 1) < epsilon:
            # Exploration: random action
            action_index = random.randint(0, len(action_space) - 1)
        else:
            # Exploitation: choose the best known action
            q_values = [Q_table.get((state, a), 0) for a in range(len(action_space))]
            max_q = max(q_values)
            # Handle multiple actions with the same max Q-value
            max_actions = [i for i, q in enumerate(q_values) if q == max_q]
            action_index = random.choice(max_actions)

        action = action_space[action_index]

        # Press the selected buttons
        for btn in action:
            if args.mode == 'train':
                pyboy.button(btn, 1)
            elif step % 5 == 0:
                pyboy.button(btn, 5)

        # Advance the game to see the effect of the action
        pyboy.tick(1)

        # Observe new state and reward
        next_state = get_state(mario)
        current_fitness = fitness_function(mario)
        reward = current_fitness - previous_fitness
        previous_fitness = current_fitness

        if args.mode == 'train':
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
            print(f"Step {step} - Level: {mario.world} - Level Progress: {mario.level_progress} - Fitness: {current_fitness:.2f} - Epsilon: {epsilon:.4f}")

        # Check for game over and reset if necessary
        if mario.lives_left < 0:
            # Reset the game
            mario.reset_game()
            state = get_state(mario)
            previous_fitness = fitness_function(mario)
except KeyboardInterrupt:
    print("Emulation interrupted by user.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    if args.mode == 'train':
        # Save Q-table
        with open('q_table.pkl', 'wb') as f:
            pickle.dump(Q_table, f)
    pyboy.stop()
