#!/usr/bin/env python3

from pyboy import PyBoy

# Initialize PyBoy with the selected ROM
rom_path = 'roms/Super Mario Land (World) (Rev A).gb'
if not rom_path:
    exit()

pyboy = PyBoy(rom_path, sound=False)
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

pyboy.tick() # To render screen after `.start_game`
pyboy.screen.image.save('SuperMarioLand1.png')

print(mario)
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

# Main emulation loop
try:
    while pyboy.tick():
        pass
except KeyboardInterrupt:
    print("Emulation interrupted by user.")
finally:
    pyboy.stop()
