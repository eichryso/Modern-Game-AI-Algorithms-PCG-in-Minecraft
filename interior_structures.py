import random
import itertools
import math
from gdpc import Block 

from inventory import material

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

def placement_loss(placements, interior_mask, wall_mask, traits):
    """
    Loss function for interior structure placement. The function evaluates the quality of a given placement of interior structures (bed, library, fireplace, living room) based on several criteria:
    1. Proximity: The function calculates the pairwise distances between all placed structures and penalizes placements that are too close together, encouraging a more spacious layout.
    2. Wall Adjacency: For structures that require wall adjacency (e.g., library, fireplace), the function checks if they are placed adjacent to a wall and penalizes placements that do not meet this requirement.
    3. Valid Placement: The function checks if all placed structures are within the valid interior area defined by the interior_mask and penalizes any placements that are outside this area.
    The loss is calculated as a combination of these factors, with higher penalties for more severe violations of the placement criteria. The function returns a numerical loss value, where lower values indicate better placements.
    Inputs:
    - placements: a dictionary mapping structure names (e.g., "bed", "library", "fireplace", "livingroom") to their (x, z) coordinates in the interior
    - interior_mask: a dictionary mapping (x, z) coordinates to a boolean indicating whether that position is valid for placement
    - wall_mask: a dictionary mapping (x, z) coordinates to a boolean indicating whether that position is adjacent to a wall
    - traits: a dictionary mapping structure names to their traits, such as whether they require wall adjacency
    Returns:
    - loss: a numerical value representing the quality of the placement, where lower values indicate better placements
    """
    loss = 0
    for (name1, pos1), (name2, pos2) in itertools.combinations(placements.items(), 2):
        dist = math.dist(pos1, pos2)
        manhattan = abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
        if manhattan <= 1:
            loss += 10000 
        loss -= dist
    for name, pos in placements.items():
        if traits[name].get("wall_required") and not wall_mask[pos]:
            loss += 100 
    for name, pos in placements.items():
        if not interior_mask[pos]:
            loss += 1000
    return loss

def scan_floor_masks(house_x, house_z, house_width, house_length, blocked_positions):
    """
    Scan the floor area of the house and create two masks: interior_mask and wall_mask. The interior_mask indicates which (x, z) positions are valid for placing interior structures, 
    while the wall_mask indicates which positions are adjacent to walls. The function takes into account any blocked positions (e.g., due to stairs or stair openings) and marks those positions as invalid in both masks. 
    The masks are returned as dictionaries mapping (x, z) coordinates to boolean values.
    Inputs:
    - house_x, house_z: the starting (x, z) coordinates of the house
    - house_width, house_length: the dimensions of the house, used to determine the area to scan for valid interior positions
    - blocked_positions: a set of (x, z) tuples representing positions that are blocked for placement (e.g., due to stairs or stair openings)
    Returns:
    - interior_mask: a dictionary mapping (x, z) coordinates to a boolean indicating whether that position is valid for placing interior structures
    - wall_mask: a dictionary mapping (x, z) coordinates to a boolean indicating whether that position is adjacent to a wall
    """
    interior_mask = {}
    wall_mask = {}
    for x in range(house_x + 1, house_x + house_length - 1):
        for z in range(house_z + 1, house_z + house_width - 1):
            pos = (x, z)
            if blocked_positions and pos in blocked_positions:
                interior_mask[pos] = False
                wall_mask[pos] = False
                continue
            interior_mask[pos] = True
            if (
                x == house_x + 1 or x == house_x + house_length - 2 or
                z == house_z + 1 or z == house_z + house_width - 2
            ):
                wall_mask[pos] = True
            else:
                wall_mask[pos] = False
    return interior_mask, wall_mask

def detect_obstacles(ED, x, floor_y, z, house_height, width, length, blocked_positions):
    """
    Detect obstacles such as doors, windows, and stairs within the floor area of the house. The function identifies these obstacles based on their expected locations (e.g., doors at the center of west/east walls, windows along the walls)
    and any additional blocked positions provided. The function returns a set of (x, z) tuples representing the positions of all detected obstacles, which can be used to mark those positions as invalid for interior structure placement.
    Inputs:
    - ED: the Editor object to scan blocks in the world
    - x, z: the starting (x, z) coordinates of the house
    - floor_y: the y-coordinate of the floor to scan for obstacles
    - house_height: the height of the house, used to determine the vertical range to scan for obstacles
    - width, length: the dimensions of the house, used to determine the area to scan for obstacles
    - blocked_positions: a set of (x, z) tuples representing additional positions to consider as obstacles (e.g., due to stairs or stair openings)
    Returns:
    - forbidden: a set of (x, z) tuples representing the positions of all detected obstacles, which should be avoided when placing interior structures
    """
    forbidden = set(blocked_positions) if blocked_positions else set()
    main_door = (x, z + width // 2)
    garden_door = (x + length - 1, z + width // 2)
    forbidden.add(main_door)
    forbidden.add(garden_door)
    window_positions = set()
    for x in range(x + 1, x + length - 1):
        window_positions.add((x, z + 1))
        window_positions.add((x, z + width - 2))
    for z in range(z + 1, z + width - 1):
        window_positions.add((x + 1, z))
        window_positions.add((x + length - 2, z))
    forbidden.update(window_positions)
    return forbidden

def bed_fits(pos, interior_mask, wall_mask):
    """
    Check if a bed can fit at the given position.
    A bed occupies two horizontal cells, and neither cell should be a wall or outside the interior.
    Inputs:
    - pos: a tuple (x, z) representing the position to check for bed placement
    - interior_mask: a dictionary mapping (x, z) coordinates to a boolean indicating whether that position is valid for placement
    - wall_mask: a dictionary mapping (x, z) coordinates to a boolean indicating whether that position is adjacent to a wall
    Returns:
    - a boolean indicating whether the bed can fit at the given position
    """
    x0, z0 = pos
    return (
        (x0, z0) in interior_mask and interior_mask[(x0, z0)] and not wall_mask.get((x0, z0), False)
        and (x0+1, z0) in interior_mask and interior_mask[(x0+1, z0)] and not wall_mask.get((x0+1, z0), False)
    )

def fireplace_fits_with_orientation(pos, interior_mask):
    """
    Check if a fireplace can fit at the given position with a specific orientation.
    A fireplace occupies three cells in either horizontal or vertical orientation.
    Inputs:
    - pos: a tuple (x, z) representing the position to check for fireplace placement
    - interior_mask: a dictionary mapping (x, z) coordinates to a boolean indicating whether that position is valid for placement
    Returns:
    - a tuple (fits, orientation) where fits is a boolean indicating whether the fireplace can fit,
      and orientation is either "horizontal", "vertical", or None if it doesn't fit
    """
    x0, z0 = pos
    horiz_cells = [(x0-1, z0), (x0, z0), (x0+1, z0)]
    vert_cells = [(x0, z0-1), (x0, z0), (x0, z0+1)]
    def all_interior(cells):
        for cell in cells:
            if cell not in interior_mask or not interior_mask[cell]:
                return False
        return True
    if all_interior(horiz_cells):
        return True, "horizontal"
    if all_interior(vert_cells):
        return True, "vertical"
    return False, None

def livingroom_fits(pos, interior_mask, wall_mask):
    """
    Check if a living room setup can fit at the given position.
    A living room setup includes a 2x2 table and a 3-cell couch.
    Inputs:
    - pos: a tuple (x, z) representing the position to check for living room placement
    - interior_mask: a dictionary mapping (x, z) coordinates to a boolean indicating whether that position is valid for placement
    - wall_mask: a dictionary mapping (x, z) coordinates to a boolean indicating whether that position is adjacent to a wall
    Returns:
    - a boolean indicating whether the living room setup can fit at the given position
    """
    x0, z0 = pos
    table_cells = [
        (x0, z0), (x0+1, z0), (x0, z0+1), (x0+1, z0+1)
    ]
    couch_cells = [
        (x0-1, z0-1), (x0-1, z0), (x0-1, z0+1)
    ]
    for cell in table_cells + couch_cells:
        if cell not in interior_mask or not interior_mask[cell] or wall_mask.get(cell, False):
            return False
    return True

def is_in_interior(px, pz, x, z, length, width):
    """
    Check if a position is within the interior boundaries.
    Inputs:
    - px, pz: the position to check
    - x, z: the top-left corner of the interior
    - length, width: the dimensions of the interior
    Returns:
    - a boolean indicating whether the position is within the interior
    """
    return (x + 1 <= px < x + length - 1) and (z + 1 <= pz < z + width - 1)
