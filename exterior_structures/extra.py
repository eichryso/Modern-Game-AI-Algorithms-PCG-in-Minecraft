import random

from gdpc import Block
from foundation.inventory import material

def place_random_crop_region_full(ED, garden_x, garden_y, garden_z, garden_length, garden_width, occupied):
    """
    Place a random rectangular crop region in the garden, avoiding occupied cells.
    Inputs:
    - ED: the Editor object to place blocks in the world
    - garden_x, garden_y, garden_z: the coordinates of the corner of the garden
    - garden_length, garden_width: the dimensions of the garden
    - occupied: a set of (x, z) tuples representing occupied cells to avoid
    Returns:
    - a tuple containing:
        - a boolean indicating whether the crop region was successfully placed
        - a set of (x, z) tuples representing the cells occupied by the crop region
        - the x and z coordinates of the corner of the crop region
        - the width and height of the crop region
        - the material used for the crop blocks
        - the material used for the floor blocks beneath the crop
    """
    
    candidates = []
    for _ in range(40):
        crop_w = random.randint(2, min(5, garden_length-2))
        crop_h = random.randint(2, min(5, garden_width-2))
        x0 = random.randint(garden_x+1, garden_x+garden_length-crop_w-1)
        z0 = random.randint(garden_z+1, garden_z+garden_width-crop_h-1)
        region = set((x, z) for x in range(x0, x0+crop_w) for z in range(z0, z0+crop_h))
        if all((x, z) not in occupied for x in range(x0, x0+crop_w) for z in range(z0, z0+crop_h)):
            candidates.append((x0, z0, crop_w, crop_h))
    crop_positions = set()
    if not candidates:
        return None
    crop_x0, crop_z0, crop_w, crop_h = random.choice(candidates)
    crop, floor = material("crop"), material("crop_floor")
    for x in range(crop_x0, crop_x0+crop_w):
        for z in range(crop_z0, crop_z0+crop_h):
            ED.placeBlock((x, garden_y, z), Block(floor))
            if (x, z) in occupied:
                continue 
            ED.placeBlock((x, garden_y+1, z), Block(crop))
            crop_positions.add((x, z))
    return (True, crop_positions, crop_x0, crop_z0, crop_w, crop_h, crop, floor)

def place_garden_flowers(ED, garden_x, garden_y, garden_z, garden_length, garden_width, occupied, density=0.2):
    """
    Randomly place flowers in non-occupied garden spots. Flowers are placed on grass blocks and require an air block above them. The function attempts to place flowers in random locations within the garden,
    ensuring they do not overlap with occupied cells or other structures.
    Inputs:
    - ED: the Editor object to place blocks in the world
    - garden_x, garden_y, garden_z: the coordinates of the corner of the garden
    - garden_length, garden_width: the dimensions of the garden
    - occupied: a set of (x, z) tuples representing occupied cells to avoid
    - density: a float representing the desired density of flowers in the garden (default is 0.2, meaning 20% of the garden area will be attempted for flower placement)
    """
    max_patch_w = min(5, garden_length-2)
    max_patch_h = min(5, garden_width-2)
    min_patch = 2
    attempts = 0
    patches_planted = 0
    max_patches = int((garden_length * garden_width * density) // (max_patch_w * max_patch_h)) + 1
    while patches_planted < max_patches and attempts < 100:
        patch_w = random.randint(min_patch, max_patch_w)
        patch_h = random.randint(min_patch, max_patch_h)
        x0 = random.randint(garden_x+1, garden_x+garden_length-patch_w-1)
        z0 = random.randint(garden_z+1, garden_z+garden_width-patch_h-1)
        can_plant = True
        for x in range(x0, x0+patch_w):
            for z in range(z0, z0+patch_h):
                if (x, z) in occupied:
                    can_plant = False
                    break
                block_above = ED.getBlock((x, garden_y+1, z))
                if str(block_above) != "minecraft:air":
                    can_plant = False
                    break
                block_below = ED.getBlock((x, garden_y, z))
                if str(block_below) == "minecraft:gravel":
                    can_plant = False
                    break
            if not can_plant:
                break
        if can_plant:
            for x in range(x0, x0+patch_w):
                for z in range(z0, z0+patch_h):
                    flower = material("flower")
                    ED.placeBlock((x, garden_y, z), Block("minecraft:grass_block"))
                    ED.placeBlock((x, garden_y+1, z), Block(flower))
            patches_planted += 1
        attempts += 1


def place_random_pond(ED, garden_x, garden_y, garden_z, garden_length, garden_width, occupied, min_pond_size=2, max_pond_size=4):
    """
    Place a rectangular pond (water blocks) of random size in the garden, avoiding occupied cells. The function attempts to find a suitable location for the pond within the garden dimensions, 
    ensuring it does not overlap with any occupied cells or structures. If a valid location is found, the pond is created by placing water blocks in the designated area.
    Inputs:
    - ED: the Editor object to place blocks in the world
    - garden_x, garden_y, garden_z: the coordinates of the corner of the garden
    - garden_length, garden_width: the dimensions of the garden
    - occupied: a set of (x, z) tuples representing occupied cells to avoid
    - min_pond_size: the minimum width and height of the pond (default is 2)
    - max_pond_size: the maximum width and height of the pond (default is 4)
    Returns:
    - a set of (x, z) tuples representing the cells occupied by the pond, which can be used for further checks when placing other features in the garden, or None if no suitable location is found
    """
    candidates = []
    for _ in range(30):
        pond_w = random.randint(min_pond_size, min(max_pond_size, garden_length-2))
        pond_h = random.randint(min_pond_size, min(max_pond_size, garden_width-2))
        x0 = random.randint(garden_x+1, garden_x+garden_length-pond_w-1)
        z0 = random.randint(garden_z+1, garden_z+garden_width-pond_h-1)
        region = set((x, z) for x in range(x0, x0+pond_w) for z in range(z0, z0+pond_h))
        if not region & occupied:
            candidates.append((x0, z0, pond_w, pond_h, region))
    if not candidates:
        return None
    x0, z0, pond_w, pond_h, region = random.choice(candidates)
    for x in range(x0, x0+pond_w):
        for z in range(z0, z0+pond_h):
            if (x, z) in occupied:
                continue
            ED.placeBlock((x, garden_y, z), Block("minecraft:water"))
    return region
