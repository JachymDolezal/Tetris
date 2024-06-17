import time
import keyboard
from colorama import Fore, Back, Style
from shapes import j_shape, i_shape, o_shape, s_shape, t_shape, z_shape, l_shape
import os
import curses



global x, y, delta, rotation, shape, grid
timer_per_fall = 8
fall_timer = 1
x = 0
y = 0
delta = 0
rotation = 0
score = 0
shapes_on_grid = {"current": {}, "next": {}, "hold": {}, "placed": []}

list_of_randomized_shapes = []

clear = ("cls" if os.name == "nt" else "clear")

GRID_W = 10
GRID_H = 20

grid = [["0" for x in range(GRID_W)] for y in range(GRID_H)]

"""
add this to the bottom of the grid
1000000000
1011101111
1011101111
1111111111
"""

grid_bottom = [
    ["1", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
    ["1", "0", "1", "1", "1", "0", "1", "1", "1", "1"],
    ["1", "0", "1", "1", "1", "0", "1", "1", "1", "1"],
    ["1", "1", "1", "1", "1", "1", "1", "1", "1", "1"],
]

grid_placed_shapes = [["0" for x in range(GRID_W)] for y in range(GRID_H)]

# add the bottom to the grid
for row in range(len(grid_bottom)):
    for col in range(len(grid_bottom[0])):
        grid[GRID_H - len(grid_bottom) + row][col] = grid_bottom[row][col]

grid_original = grid

shape = l_shape["shape"]
shapes_on_grid["current"] = {
    "shape": l_shape["shape"],
    "x": 0,
    "y": 0,
    "rotation": 0,
    "data": l_shape,
}
shapes_on_grid["next"] = {
    "shape": l_shape["shape"],
    "x": 0,
    "y": 0,
    "rotation": 0,
    "data": l_shape,
}

# create sample placed shapes
shapes_on_grid["placed"].append({"shape": l_shape, "x": 7, "y": 17})
shapes_on_grid["placed"].append({"shape": l_shape, "x": 5, "y": 17})
shapes_on_grid["placed"].append({"shape": l_shape, "x": 4, "y": 17})


def place_shape(shape, x, y):
    for row in range(len(shape)):
        for col in range(len(shape[0])):
            if shape[row][col] != "0":
                grid[y + row][x + col] = shape[row][col]


# def draw_grid():

#     for row in grid:
#         print("|"+''.join(row)+"|")


def draw_grid(stdscr, score):
    stdscr.clear()
    print("--")
    # print("next shape")
    # for row in shapes_on_grid["next"]["shape"]:
    #     for cell in row:
    #         if cell == "0":
    #             print(Fore.BLACK + Back.WHITE + " " + Style.RESET_ALL, end="")
    #         if cell == "1":
    #             print(Fore.BLACK + Back.GREEN + " " + Style.RESET_ALL, end="")
    #     print()
    # print("+----------+")
    # for row in grid:
    #     print("|", end="")
    #     for cell in row:
    #         if cell == "0":
    #             print(Fore.BLACK + Back.WHITE + " " + Style.RESET_ALL, end="")
    #         if cell == "1":
    #             print(Fore.BLACK + Back.GREEN + " " + Style.RESET_ALL, end="")
    #     print("|", end="")
    #     print()
    # print("+---------+")
    # print("Score:", score)
    # print next shape
    stdscr.addstr(0, 15, "Next shape", curses.color_pair(1))
    for y, row in enumerate(shapes_on_grid["next"]["shape"]):
        for x, val in enumerate(row):
            if val == "0":
                stdscr.addstr(y+2, x + 15, ".", curses.color_pair(1))
            if val == "1":
                stdscr.addstr(y+2, x + 15, " ", curses.color_pair(2))

    # print rotation indicator
    stdscr.addstr(5, 15, "Rotation: " + str(shapes_on_grid["current"]["rotation"]), curses.color_pair(1))

    # print score
    stdscr.addstr(19, 15, "Score: " + str(score), curses.color_pair(1))
    # print boarder top
    for x in range(0, 9):
        stdscr.addstr(0, x, "-", curses.color_pair(1))
    for y, row in enumerate(grid):
        for x, val in enumerate(row):
            if val == "0":
                stdscr.addstr(y, x, ".", curses.color_pair(1))
            if val == "1":
                stdscr.addstr(y, x, " ", curses.color_pair(2))
    stdscr.refresh()


def rotate_shape(shape, rotation, data):
    print("rotating", shape, rotation)
    # get number of keys in the data dictionary
    keys = len(data.keys())
    rotation = (rotation + 1) % keys
    shape = data[list(data.keys())[rotation]]

    print("rotating", shape, rotation)

    return shape, rotation


# Dictionary to track currently pressed keys and their state
key_states = {"left": False, "right": False, "c": False, "down": False}


def clear_the_grid():
    global grid
    grid = [["0" for x in range(GRID_W)] for y in range(GRID_H)]

# Define the actions for the game
def move_left():
    global x
    if check_collision_side(shapes_on_grid["current"], -1):
        return
    shapes_on_grid["current"]["x"] -= 1


def move_right():
    global x
    if check_collision_side(shapes_on_grid["current"], 1):
        return
    shapes_on_grid["current"]["x"] += 1


def rotate():
    global shape, rotation
    shapes_on_grid["current"]["shape"], rotation = rotate_shape(
        shapes_on_grid["current"]["shape"], shapes_on_grid["current"]["rotation"], shapes_on_grid["current"]["data"]
    )
    shapes_on_grid["current"]["rotation"] = rotation


def drop():
    global y
    shapes_on_grid["current"]["y"] += 1


def get_top_level(grid):
    # Initialize the top_level list with None values
    top_level = [None] * GRID_W

    # Iterate over the grid rows
    for y in range(GRID_H):
        for x in range(GRID_W):
            if grid[y][x] != "0" and top_level[x] is None:
                top_level[x] = y

    # Replace None values with GRID_H to indicate no cells are occupied in those columns
    for i in range(GRID_W):
        if top_level[i] is None:
            top_level[i] = GRID_H

    print(top_level)
    # if one of the columns is zero return True
    if 0 in top_level:
        return None
    return top_level


def check_collision(shape, top_level_coords):

    # if a non-zero cell in the shape has y coordinate greater or equal to the top level coordinate of the same column return True
    for row in range(len(shape["shape"])):
        for col in range(len(shape["shape"][0])):
            if (
                shape["shape"][row][col] != "0"
                and shape["y"] + row >= top_level_coords[shape["x"] + col]
            ):
                return True

    return False


def check_collision_side(shape, direction):
    # check if the shape is colliding with the sides of the grid
    for row in range(len(shape["shape"])):
        for col in range(len(shape["shape"][0])):
            if shape["shape"][row][col] != "0" and (
                shape["x"] + col + direction < 0
                or shape["x"] + col + direction >= GRID_W
            ):
                return True
    # check if the shape is colliding with the placed shapes
    for row in range(len(shape["shape"])):
        for col in range(len(shape["shape"][0])):
            if (
                shape["shape"][row][col] != "0"
                and grid_placed_shapes[shape["y"] + row][shape["x"] + col + direction]
                != "0"
            ):
                return True


# Define callback functions for key press and release events
def on_key_press(event):
    if event.name in key_states and not key_states[event.name]:
        key_states[event.name] = True
        if event.name == "left":
            move_left()
        elif event.name == "right":
            move_right()
        elif event.name == "c":
            rotate()
        elif event.name == "down":
            drop()


def on_key_release(event):
    if event.name in key_states:
        key_states[event.name] = False


def draw_placed_shapes():
    # copy grid_placed_shapes to grid
    for row in range(GRID_H):
        for col in range(GRID_W):
            grid[row][col] = grid_placed_shapes[row][col]


def add_shape_to_grid(shape, grid_placed_shapes):
    global score
    # check for index out of range
    # subtract 1 from the y coordinate of the shape
    shape["y"] -= 1
    for row in range(len(shape["shape"])):
        for col in range(len(shape["shape"][0])):
            if shape["shape"][row][col] != "0":
                # if the row or col are the last row or col of the place it -1
                grid_placed_shapes[shape["y"] + row][shape["x"] + col] = shape["shape"][
                    row
                ][col]


import random


def choose_random_shape():
    global shapes_on_grid, list_of_randomized_shapes
    if len(list_of_randomized_shapes) == 0:
        list_of_randomized_shapes = [
            j_shape,
            i_shape,
            o_shape,
            s_shape,
            t_shape,
            z_shape,
            l_shape,
        ]
        random.shuffle(list_of_randomized_shapes)
    random_shape = list_of_randomized_shapes.pop()
    # random_shape = random.choice([j_shape, i_shape, o_shape, s_shape, t_shape, z_shape, l_shape])
    shapes_on_grid["current"]["shape"] = shapes_on_grid["next"]
    shapes_on_grid["next"] = {
        "shape": random_shape["shape"],
        "x": 0,
        "y": 0,
        "rotation": 0,
        "data": random_shape,
    }


# Register the callback functions for the keys used in the game
keyboard.on_press(on_key_press)
keyboard.on_release(on_key_release)


def check_full_rows():
    global grid_placed_shapes
    points = 0
    # search the list from the bottom to the top
    for row in range(GRID_H - 1, -1, -1):
        if "0" not in grid_placed_shapes[row]:
            # print("full row", row)
            grid_placed_shapes.pop(row)
            grid_placed_shapes.insert(0, ["0" for x in range(GRID_W)])
            points += 10
            # clear_the_grid()
            # draw_grid()
    # add multiplier for each row
    points = points * points
    return points


place_shape(shapes_on_grid["current"]["shape"], 0, 0)

placed = False




# Main game loop
def main_game_loop(stdscr):
    global x, y, delta, rotation, shape, grid, placed, score, timer_per_fall
    curses.curs_set(0)  # Hide the cursor
    stdscr.nodelay(1)   # Don't block waiting for user input
    stdscr.timeout(100) # Refresh every 100ms

    repetitions = 0

    # Initialize colors
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)  # White on black
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_RED)  # Black on white
    print("Game started. Press ESC to stop.")
    while True:
        clear_the_grid()
        # Explicitly check for key release events
        for key in key_states.keys():
            if not keyboard.is_pressed(key):
                key_states[key] = False

        draw_placed_shapes()
        # check if the current shape is colliding with any of the placed shapes
        top_level_coords = get_top_level(grid)
        if top_level_coords is None:
            print("game over")
            break
        if check_collision(shapes_on_grid["current"], top_level_coords):
            print("Collision detected")
            add_shape_to_grid(shapes_on_grid["current"], grid_placed_shapes)
            choose_random_shape()
            shapes_on_grid["current"] = {
                "shape": shapes_on_grid["next"]["shape"],
                "x": 0,
                "y": 0,
                "rotation": 0,
                "data": shapes_on_grid["next"]["data"],
            }
            print("current shape", shapes_on_grid["current"]["rotation"])
            placed = True
            points = check_full_rows()

            score += points
            # place the current shape to placed shapes and reset the current shape
        else:
            place_shape(
                shapes_on_grid["current"]["shape"],
                shapes_on_grid["current"]["x"],
                shapes_on_grid["current"]["y"],
            )

        delta += 1
        if delta == timer_per_fall:
            # clear_the_grid()
            shapes_on_grid["current"]["y"] += 1
            delta = 0
            repetitions += 1
        # time.sleep(0.0001)
        if repetitions == 50:
            repetitions = 0
            timer_per_fall -= 1
            if timer_per_fall < 8:
                timer_per_fall = 8
            print("speeding up", timer_per_fall)
        draw_grid(stdscr=stdscr, score=score)
        # clear screen
        # print("\033[H\033[J")
        # clear
        time.sleep(0.001)
        # os.system(clear)
        # print(chr(27) + "[2J")
        # time.sleep(0.0001)
        if placed:
            check_full_rows()
            placed = False
            continue
        # Check if ESC is pressed to exit the game
        if keyboard.is_pressed("esc"):
            break


# Run the main game loop
# main_game_loop()

curses.wrapper(main_game_loop)

print("Game over.")
