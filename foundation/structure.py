import random
from gdpc import Block
from foundation.inventory import material

def build_foundation(
    ED, Block, house_x, house_y, house_z, house_length, house_width,
    material=None, upper_floor=False, stair_positions=None, floor=None, house_height=None, floor_y=None
):
    """
    Build the foundation (floor) of the house.
    If upper_floor is True, stair_positions, floor, house_height, and floor_y must be provided.
    Inputs:
    - ED: Editor instance.
    - Block: Block class for placing
    - house_x, house_y, house_z: Coordinates of the house origin.
    - house_length, house_width: Dimensions of the house.
    - material: Optional material for the foundation. If None, a default will be used.
    - upper_floor: If True, builds the foundation for an upper floor, which includes creating openings for stairs based on stair_positions.
    - stair_positions: A dictionary containing the positions of stairs for each floor, used to create openings in the foundation for upper floors.
    - floor: The current floor number being built (0-indexed).
    - house_height: The total height of the house, used to determine stair dimensions.
    - floor_y: The y-coordinate for the current floor, used to place the foundation at the correct height.

    """
    if material is None:
        material = material("foundation")
    if upper_floor:
        stair_openings = set()
        prev_stair = stair_positions.get(floor-1)
        if prev_stair is not None and floor > 0:
            prev_stair_x, prev_stair_z = prev_stair
            stairs_len = house_height
            min_z = house_z
            stair_z_start = prev_stair_z - (stairs_len - 1)
            if stair_z_start < min_z:
                stair_z_start = min_z
            for i in range(stairs_len):
                so_z = stair_z_start + i
                stair_openings.add((prev_stair_x, so_z))
            last_stair_z = stair_z_start + stairs_len
            stair_openings.add((prev_stair_x, last_stair_z))
        prev_dims = stair_positions.get('prev_dims')
        if prev_dims is not None:
            for fx in range(prev_dims['x'], prev_dims['x'] + prev_dims['length']):
                for fz in range(prev_dims['z'], prev_dims['z'] + prev_dims['width']):
                    if (fx, fz) in stair_openings:
                        continue
                    ED.placeBlock((fx, floor_y, fz), Block(material))
    else:
        for i in range(house_length):
            for j in range(house_width):
                ED.placeBlock((house_x + i, house_y, house_z + j), Block(material))


def build_walls(ED, Block, house_x, house_y, house_z, house_height, house_width, house_length, material=None):
    """
    Build the outer walls of the house. 
    Inputs:
    - ED: Editor instance.
    - Block: Block class for placing
    - house_x, house_y, house_z: Coordinates of the house origin.
    - house_height, house_width, house_length: Dimensions of the house.
    - material: Optional material for the walls. If None, a default will be used.
    """
    if material is None:
        material = material("wall")
    for x in range(house_length):
        for z in range(house_width):
            for y in range(1, house_height):
                if x == 0 or x == house_length - 1 or z == 0 or z == house_width - 1:
                    ED.placeBlock((house_x + x, house_y + y, house_z + z), Block(material))
                else:
                    ED.placeBlock((house_x + x, house_y + y, house_z + z), Block("minecraft:air"))


def build_roof(ED, Block, house_x, house_y, house_z, house_height, house_width, house_length, material=None):
    """
    Build a stepped roof: each layer is a rectangle, decreasing in size, placed one above the other.
    Inputs:
    - ED: Editor instance.
    - Block: Block class for placing
    - house_x, house_y, house_z: Coordinates of the house origin.
    - house_height, house_width, house_length: Dimensions of the house.
    - material: Optional material for the roof. If None, a default will be used.
    """
    if material is None:
        material = material("roof")
    num_layers = min(4, (min(house_length, house_width) // 2))
    for layer in range(num_layers):
        layer_x_start = house_x + layer - 1
        layer_x_end = house_x + house_length - layer + 1
        layer_z_start = house_z + layer - 1
        layer_z_end = house_z + house_width - layer + 1
        layer_y = house_y + house_height + layer
        for x in range(layer_x_start, layer_x_end):
            for z in range(layer_z_start, layer_z_end):
                ED.placeBlock((x, layer_y, z), Block(material))



def build_stairs(ED, house_x, house_y, house_z, house_height, house_width, house_length, stair_x=None, stair_z=None, stair_material=None):
    """
    Place stairs between two floors in the house, optionally at a specified position.
    Returns the (x, z) position of the stairs for overlap checking.
    Args:
        ED: Editor instance.
        house_x, house_y, house_z: Coordinates of the house origin.
        house_height, house_width, house_length: Dimensions of the house.
        stair_x, stair_z: Optional coordinates for stair placement.
    Returns:
        (stair_x, stair_z): The position of the stairs.
    """
    if stair_material is None:
        stair_material = material("stairs")
    stairs_len = house_height - 1
    margin = 0
    min_x = house_x + margin
    max_x = house_x + house_length - margin - 1
    min_z = house_z + margin
    max_z = house_z + house_width - margin - 1
    if stair_x is None:
        stair_x = random.randint(min_x, max_x)
    else:
        stair_x = max(min_x, min(stair_x, max_x))
    if stair_z is None:
        stair_z = random.randint(min_z + stairs_len - 1, max_z)
    else:
        stair_z = max(min_z + stairs_len - 1, min(stair_z, max_z))
    stair_z_start = stair_z - (stairs_len - 1)
    if stair_z_start < min_z:
        stair_z_start = min_z
        stair_z = stair_z_start + stairs_len - 1
    for i in range(stairs_len):
        y = house_y + 1 + i
        z = stair_z_start + i
        if not (min_z <= z <= max_z):
            continue
        ED.placeBlock((stair_x, y, z), Block(stair_material, {"facing": "south"}))
        ED.placeBlock((stair_x, y + 1, z), Block("minecraft:air"))
        ED.placeBlock((stair_x, y + 2, z), Block("minecraft:air"))
    y = house_y + 1 + stairs_len
    z = stair_z_start + stairs_len
    if min_z <= z <= max_z:
        ED.placeBlock((stair_x, y, z), Block(stair_material, {"facing": "south"}))
        ED.placeBlock((stair_x, y + 1, z), Block("minecraft:air"))
        ED.placeBlock((stair_x, y + 2, z), Block("minecraft:air"))
    opening_y1 = house_y + house_height
    opening_y2 = house_y + house_height + 1
    for i in range(stairs_len):
        z = stair_z_start + i
        if not (min_z <= z <= max_z):
            continue
        ED.placeBlock((stair_x, opening_y1, z), Block("minecraft:air"))
        ED.placeBlock((stair_x, opening_y2, z), Block("minecraft:air"))
    return stair_x, stair_z




def build_windows(ED, house_x, house_y, house_z, house_height, house_width, house_length):
    """
    Place windows on all four sides of the house for each floor. Windows are randomly sized and positioned, but will not block the main door or garden door on the ground floor,
    and will be placed at reasonable heights on upper floors. The number of windows per wall is determined by the wall length, with a maximum of 4 windows per wall to avoid 
    overcrowding. Windows are centered on the walls when possible, and will not be placed if the wall is too short to accommodate them.
    Inputs:
    - ED: Editor instance.
    - house_x, house_y, house_z: Coordinates of the house origin.
    - house_height, house_width, house_length: Dimensions of the house.
    """
    if not hasattr(build_windows, "window_material"):
        build_windows.window_material = material("window")
        build_windows.window_width = random.randint(2, 4)
        build_windows.window_height = random.randint(2, 4)
    window_material = build_windows.window_material
    window_width = build_windows.window_width
    window_height = build_windows.window_height
    for floor in range(house_height):
        min_y = house_y + 1 if floor == 0 else house_y + 2
        max_y = house_y + house_height - window_height - 1
        window_y = min_y if max_y < min_y else (min_y if floor == house_height - 1 else random.randint(min_y, max_y))
        for wall_z in [house_z, house_z + house_width - 1]:
            wall_len = house_length - 2
            num_windows = min(4, wall_len // (window_width + 1))
            if num_windows < 1:
                continue
            total_window_space = num_windows * window_width + (num_windows - 1)
            start_x = house_x + 1 + (wall_len - total_window_space) // 2
            for w in range(num_windows):
                door_x = house_x + house_length // 2
                window_x_start = start_x + w * (window_width + 1)
                window_x_end = window_x_start + window_width
                margin = 1
                if (window_x_start - margin <= door_x < window_x_end + margin):
                    continue
                for wx in range(window_width):
                    for wy in range(window_height):
                        y = window_y + wy
                        ED.placeBlock((window_x_start + wx, y, wall_z), Block(window_material))
        for wall_x in [house_x, house_x + house_length - 1]:
            wall_len = house_width - 2
            num_windows = min(4, wall_len // (window_width + 1))
            if num_windows < 1:
                continue
            total_window_space = num_windows * window_width + (num_windows - 1)
            start_z = house_z + 1 + (wall_len - total_window_space) // 2
            for w in range(num_windows):
                door_z = house_z + house_width // 2
                window_z_start = start_z + w * (window_width + 1)
                window_z_end = window_z_start + window_width
                margin = 1
                if wall_x == house_x:
                    if (window_z_start - margin <= door_z + 1 < window_z_end + margin) or (window_z_start - margin <= door_z - 1 < window_z_end + margin) or (window_z_start - margin <= door_z < window_z_end + margin):
                        continue
                else:
                    if (window_z_start - margin <= door_z < window_z_end + margin):
                        continue
                for wz in range(window_width):
                    for wy in range(window_height):
                        y = window_y + wy
                        ED.placeBlock((wall_x, y, window_z_start + wz), Block(window_material))

