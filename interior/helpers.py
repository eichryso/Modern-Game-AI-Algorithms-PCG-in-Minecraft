import itertools
import math

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
