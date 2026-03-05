import random
from gdpc import Block 

from foundation.inventory import material

def build_bed(ED, house_x, house_y, house_z, house_height, house_width, house_length, blocked_positions):
    """
    Place a bed at the given (house_x, house_y, house_z) position, using absolute coordinates. The bed consists of a head and foot block, which are placed next to each other. 
    The function checks if the blocks at the intended positions are replaceable (air, carpet, or snow) before placing the bed to avoid overwriting important structures. 
    Inputs:
    - ED: the Editor object to place blocks in the world
    - house_x, house_y, house_z: the coordinates of the bed head (absolute world coordinates)
    """
    bed_material = material("bed")
    def is_replaceable(block_id):
        return (
            block_id.endswith("air")
            or "carpet" in block_id
            or block_id == "minecraft:snow"
            or "bed" in block_id
        )
    ED.placeBlock((house_x, house_y+1, house_z), Block(bed_material, {"facing": "east", "occupied": "false"}))

def build_fireplace(ED, house_x, house_y, house_z, house_height, house_width, house_length, blocked_positions=None, orientation="horizontal"):
    """
    Place a fireplace at the given (house_x, house_y, house_z) position, using absolute coordinates. The fireplace consists of a campfire block with a surrounding structure made of foundation material. 
    The orientation parameter determines the layout of the fireplace (horizontal or vertical).
    Inputs:
    - ED: the Editor object to place blocks in the world
    - house_x, house_y, house_z: the coordinates of the fireplace center (absolute world coordinates)
    - orientation: a string that can be either "horizontal" or "vertical", determining the layout of the fireplace
    """
    floor_y = house_y + 1
    mat_material = material("foundation")
    mat = Block(mat_material)
    if orientation == "horizontal":
        for dx in [-1, 0, 1]:
            ED.placeBlock((house_x + dx, floor_y, house_z), mat)
        ED.placeBlock((house_x - 1, floor_y + 1, house_z), mat)
        ED.placeBlock((house_x + 1, floor_y + 1, house_z), mat)
        ED.placeBlock((house_x, floor_y, house_z), Block("minecraft:campfire"))
        for dy in range(1, 4):
            ED.placeBlock((house_x, floor_y + dy, house_z), mat)
    elif orientation == "vertical":
        for dz in [-1, 0, 1]:
            ED.placeBlock((house_x, floor_y, house_z + dz), mat)
        ED.placeBlock((house_x, floor_y + 1, house_z - 1), mat)
        ED.placeBlock((house_x, floor_y + 1, house_z + 1), mat)
        ED.placeBlock((house_x, floor_y, house_z), Block("minecraft:campfire"))
        for dy in range(1, 4):
            ED.placeBlock((house_x, floor_y + dy, house_z), mat)

def build_library(ED, house_x, house_y, house_z, house_height, house_width, house_length, blocked_positions=None):
    """
    Place a bookshelf (library) at the given (house_x, house_y, house_z) position, using absolute coordinates. The bookshelf is a vertical stack of bookshelf blocks up to the height of the house. 
    The function does not check for replaceable blocks, so it assumes the caller has ensured the area is suitable for placement.
    Inputs:
    - ED: the Editor object to place blocks in the world
    - house_x, house_y, house_z: the coordinates of the bookshelf base (absolute world coordinates)
    - house_height: the height of the house, determining how many bookshelf blocks to stack
    """
    bookshelf_material = material("bookshelf")
    bookshelf_block = Block(bookshelf_material)
    for dy in range(house_height):
        ED.placeBlock((house_x, house_y + 1 + dy, house_z), bookshelf_block)

def build_living_room(ED, house_x, house_y, house_z, house_height, house_width, house_length, blocked_positions=None):
    """
    Place a living room (table and couch) at the given (house_x, house_y, house_z) position, using absolute coordinates. The living room consists of a 2x2 table made of foundation material and a couch made of stairs blocks.
    The table is placed at the center of the living room area, and the couch is placed to the west of the table with one empty cell between them. The function checks for blocked positions to avoid placing furniture in those locations.
    Inputs:
    - ED: the Editor object to place blocks in the world
    - house_x, house_y, house_z: the coordinates of the living room area (absolute world coordinates)
    - house_height, house_width, house_length: the dimensions of the house, used to determine the placement of the table and couch
    - blocked_positions: a set of (x, z) tuples representing positions to avoid when placing furniture (e.g., stairs or door openings)
    """
    floor_y = house_y + 1
    table_material = material("foundation")
    table_block = Block(table_material)
    for dx in [0, 1]:
        for dz in [0, 1]:
            ED.placeBlock((house_x + dx, floor_y, house_z + dz), table_block)
    couch_block_material = material("stairs")
    couch_block = Block(couch_block_material, {"facing": "west", "half": "bottom"})
    for dz in [-1, 0, 1]:
        ED.placeBlock((house_x - 2, floor_y, house_z + dz), couch_block)

def build_carpet(ED, house_x, house_y, house_z, house_height, house_width, house_length, blocked_positions=None):
    """
    Place carpets on the floor, avoiding blocked positions (e.g., stairs). The function attempts to place carpets in random rectangular regions on the floor, ensuring that they do not overlap with any blocked positions.
    The carpets are placed on the floor level (house_y + 1) and are made of a material defined in the material function. The function uses a random approach to create a more natural
    carpet layout, with a maximum number of attempts to place carpets to prevent infinite loops.
    Inputs:
    - ED: the Editor object to place blocks in the world
    - house_x, house_y, house_z: the coordinates of the house (absolute world coordinates)
    - house_height, house_width, house_length: the dimensions of the house, used to determine the floor area for carpet placement
    - blocked_positions: a set of (x, z) tuples representing positions to avoid when placing carpets (e.g., stairs or door openings)
    """
    floor_y = house_y + 1
    x0, x1 = house_x + 1, house_x + house_length - 2
    z0, z1 = house_z + 1, house_z + house_width - 2
    carpet_material = material("carpet")
    if blocked_positions is None:
        blocked_positions = set()
    occupied = set(blocked_positions)
    max_rects = random.randint(2, 15)
    rects_placed = 0
    attempts = 0
    while rects_placed < max_rects and attempts < 50:
        w = random.randint(min(4, x1-x0+1), min(4, x1-x0+1))
        l = random.randint(min(4, z1-z0+1), min(4, z1-z0+1))
        rx = random.randint(x0, x1 - w + 1)
        rz = random.randint(z0, z1 - l + 1)
        region = [(x, z) for x in range(rx, rx + w) for z in range(rz, rz + l)]
        if any((x, z) in occupied for (x, z) in region):
            attempts += 1
            continue
        if any(ED.getBlock((x, floor_y-1, z)).id.endswith("air") for (x, z) in region):
            attempts += 1
            continue
        for (x, z) in region:
            ED.placeBlock((x, floor_y, z), Block(carpet_material))
            occupied.add((x, z))
        rects_placed += 1
        attempts += 1

def build_int_lights(ED, house_x, house_y, house_z, house_height, house_width, house_length, blocked_positions=None, is_top_floor=False):
    """
    Add lights at the four inner corners of the house, avoiding blocked positions. The function places hanging lights one block below the ceiling/floor above for all floors.
    The light material is defined in the material function, and the function checks if the intended light positions are within the floor bounds and not in the blocked positions before placing the lights. The function is
    designed to be called for each floor, and it can be configured to avoid placing lights on the top floor if desired.
    Inputs:
    - ED: the Editor object to place blocks in the world
    - house_x, house_y, house_z: the coordinates of the house (absolute world coordinates)
    - house_height, house_width, house_length: the dimensions of the house, used to determine the light placement positions
    - blocked_positions: a set of (x, z) tuples representing positions to avoid when placing lights (e.g., stairs or door openings)
    - is_top_floor: a boolean indicating whether the current floor is the top floor, which can be used to avoid placing lights if desired (default is False)
    """
    light_material = material("light")
    light_x1 = house_x + 3
    light_x2 = house_x + house_length - 4
    light_z1 = house_z + 3
    light_z2 = house_z + house_width - 4
    light_y = house_y + house_height - 1
    if blocked_positions is None:
        blocked_positions = set()
    corners = [(light_x1, light_z1), (light_x1, light_z2), (light_x2, light_z1), (light_x2, light_z2)]
    placed = 0
    for lx, lz in corners:
        if not (house_x + 1 <= lx < house_x + house_length - 1 and house_z + 1 <= lz < house_z + house_width - 1):
            continue
        if (lx, lz) in blocked_positions:
            continue
        ED.placeBlock((lx, light_y, lz), Block(light_material, {"hanging": "true"}))
        placed += 1



