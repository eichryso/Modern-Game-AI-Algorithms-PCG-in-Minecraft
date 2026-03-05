import random

from interior.interior_structures import build_bed, build_library, build_living_room, build_fireplace, build_carpet, build_int_lights
from interior.helpers import placement_loss, scan_floor_masks, detect_obstacles, bed_fits, fireplace_fits_with_orientation, livingroom_fits, is_in_interior

def build_furniture(ED, dims, floor_y, house_height, blocked_positions=None, is_top_floor=False):
    """
    Place furniture in the house interior based on the given dimensions and floor level. The function first scans the floor for valid positions for different types of furniture (bed, library, fireplace, living room) 
    while considering blocked positions (e.g., due to stairs or openings). It then uses a random sampling approach to find a good placement of furniture that minimizes a loss function based on proximity to walls and other traits. 
    Finally, it builds the furniture in the world using the best placement found.
    Inputs:
    - ED: the Editor object to place blocks in the world
    - dims: a dictionary containing the dimensions of the house, with keys 'x', 'z', 'width', and 'length'
    - floor_y: the y-coordinate of the floor to place furniture on
    - house_height: the height of each floor of the house, used for determining the vertical placement of furniture
    - blocked_positions: a set of (x, z) tuples representing positions that are blocked for placement (e.g., due to stairs or stair openings)
    - is_top_floor: a boolean indicating whether the current floor is the top floor of the house, which can influence the placement of certain furniture (e.g., avoid placing beds on the top floor)
    """
    if blocked_positions is None:
        blocked_positions = set()
    x = dims['x']
    z = dims['z']
    width = dims['width']
    length = dims['length']
    interior_mask, wall_mask = scan_floor_masks(x, z, width, length, blocked_positions)
    forbidden = detect_obstacles(ED, x, floor_y, z, house_height, width, length, blocked_positions)
    for pos in forbidden:
        if pos in interior_mask:
            interior_mask[pos] = False
        if pos in wall_mask:
            wall_mask[pos] = False
    valid_positions = [pos for pos, ok in interior_mask.items() if ok and is_in_interior(*pos, x, z, length, width)]
    wall_positions = [pos for pos, ok in wall_mask.items() if ok and is_in_interior(*pos, x, z, length, width)]
    bed_positions = [pos for pos in valid_positions if bed_fits(pos, interior_mask, wall_mask)]
    fireplace_positions_with_orientation = []
    for pos in valid_positions:
        ok, orient = fireplace_fits_with_orientation(pos, interior_mask)
        if ok:
            fireplace_positions_with_orientation.append((pos, orient))
    fireplace_positions = [pos for (pos, orient) in fireplace_positions_with_orientation]
    fireplace_orientations = {pos: orient for (pos, orient) in fireplace_positions_with_orientation}
    livingroom_positions = [pos for pos in valid_positions if livingroom_fits(pos, interior_mask, wall_mask)]
    traits = {
        "bed": {"wall_required": False},
        "library": {"wall_required": True},
        "fireplace": {"wall_required": True},
        "livingroom": {"wall_required": False}
    }
    structure_names = ["bed", "library", "fireplace", "livingroom"]
    structure_to_positions = {
        "bed": bed_positions,
        "library": wall_positions if wall_positions else valid_positions,
        "fireplace": fireplace_positions if fireplace_positions else wall_positions if wall_positions else valid_positions,
        "livingroom": livingroom_positions
    }
    best_loss = float("inf")
    best_placement = None
    max_samples = 5000
    for _ in range(max_samples):
        try:
            bx, bz = random.choice(structure_to_positions["bed"])
            lx, lz = random.choice(structure_to_positions["library"])
            fx, fz = random.choice(structure_to_positions["fireplace"])
            vx, vz = random.choice(structure_to_positions["livingroom"])
            combo = [(bx, bz), (lx, lz), (fx, fz), (vx, vz)]
            if len(set(combo)) < 4:
                continue
            placements = dict(zip(structure_names, combo))
            loss = placement_loss(placements, interior_mask, wall_mask, traits)
            if loss < best_loss:
                best_loss = loss
                best_placement = placements
        except IndexError:
            continue
    build_carpet(ED, x, floor_y, z, house_height, width, length, blocked_positions)
    build_int_lights(ED, x, floor_y, z, house_height, width, length, blocked_positions=blocked_positions, is_top_floor=is_top_floor)
    if best_placement:
        bx, bz = best_placement["bed"]
        build_bed(ED, bx, floor_y, bz, house_height, width, length, blocked_positions)
        lx, lz = best_placement["library"]
        build_library(ED, lx, floor_y, lz, house_height, width, length, blocked_positions=blocked_positions)
        fx, fz = best_placement["fireplace"]
        fireplace_orientation = fireplace_orientations.get((fx, fz), "horizontal")
        build_fireplace(ED, fx, floor_y, fz, house_height, width, length, blocked_positions=blocked_positions, orientation=fireplace_orientation)
        vx, vz = best_placement["livingroom"]
        build_living_room(ED, vx, floor_y, vz, house_height, width, length, blocked_positions=blocked_positions)
    else:
        pass