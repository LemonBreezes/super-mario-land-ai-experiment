#!/usr/bin/env python3

from pyboy import PyBoy, WindowEvent, GBButton

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

buttons = {
    GBButton.RIGHT: False,
    GBButton.LEFT: False,
    GBButton.A: False,
    GBButton.B: False,
    GBButton.SELECT: False,
    GBButton.START: False,
    GBButton.UP: False,
    GBButton.DOWN: False,
}


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
        # Always hold down the RIGHT and B buttons to run right
        buttons[GBButton.RIGHT] = True
        buttons[GBButton.B] = True  # Hold B to run

        # Get Mario's current position
        mario_x, mario_y = mario.position

        # Check for obstacles ahead
        # For example, check tiles one space ahead and at Mario's height and slightly below
        obstacle_ahead = (
            mario.get_tile_at_pixel(mario_x + 16, mario_y) != 0 or
            mario.get_tile_at_pixel(mario_x + 16, mario_y + 16) != 0
        )

        # If there's an obstacle, press the A button to jump
        if obstacle_ahead:
            buttons[GBButton.A] = True
        else:
            buttons[GBButton.A] = False

        # Send the button inputs to PyBoy
        for button, pressed in buttons.items():
            if pressed:
                pyboy.send_input(button)
            else:
                pyboy.release_input(button)
except KeyboardInterrupt:
    print("Emulation interrupted by user.")
finally:
    pyboy.stop()
