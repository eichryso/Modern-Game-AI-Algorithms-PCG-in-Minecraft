import random
from inventory import material
from gdpc import Block, Editor

FLOOR_MATERIAL = material("foundation")
WALL_MATERIAL = material("wall")
ROOF_MATERIAL = material("roof")

ED = Editor(buffering=True)

def tree(ED, x, y, z, size):
    """
    Place a tree at the given coordinates with the specified size. The tree consists of a trunk made of wood blocks and a bushy canopy made of bush blocks.
    The trunk height is determined by the size parameter, and the canopy is a sphere or cube of bush blocks around the top of the trunk. 
    The function ensures that the canopy does not exceed the specified size and that the trunk is properly placed.
    Inputs:
    - ED: the Editor object to place blocks in the world
    - x, y, z: the coordinates of the base of the tree
    - size: the size of the tree, determining the height of the trunk and the radius of the canopy
    """
    wood = material("wood")
    bush = material("bush")
    trunk_height = size
    bush_radius = max(2, size // 2)
    # Trunk
    for i in range(trunk_height):
        ED.placeBlock((x, y + i, z), Block(wood))
    # Bush
    for dx in range(-bush_radius, bush_radius + 1):
        for dz in range(-bush_radius, bush_radius + 1):
            for dy in range(-bush_radius, bush_radius + 1):
                dist = (dx ** 2 + dz ** 2 + dy ** 2) ** 0.5
                if dist <= bush_radius:
                    ED.placeBlock((x + dx, y + trunk_height + dy, z + dz), Block(bush))

def bush(ED, x, y, z, size):
    """
    Place a bush at the given coordinates with the specified size. The bush can be either a sphere or a cube of bush blocks.
    The function ensures that the bush does not exceed the specified size and that the garden floor is properly placed beneath the bush.
    Inputs:
    - ED: the Editor object to place blocks in the world
    - x, y, z: the coordinates of the base of the bush
    - size: the size of the bush, determining the radius of the bush
    """
    bush_material = material("bush")
    garden_floor = material("garden_floor")
    shape = random.choice(["sphere", "cube"])
    placed_blocks = set()
    if shape == "sphere":
        radius = size // 2
        for dx in range(-radius, radius + 1):
            for dz in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    dist = (dx ** 2 + dz ** 2 + dy ** 2) ** 0.5
                    if dist <= radius:
                        bx, by, bz = x + dx, y + dy, z + dz
                        ED.placeBlock((bx, by, bz), Block(bush_material))
                        placed_blocks.add((bx, by, bz))
    else: 
        for dx in range(-size // 2, size // 2 + 1):
            for dz in range(-size // 2, size // 2 + 1):
                for dy in range(0, size):
                    bx, by, bz = x + dx, y + dy, z + dz
                    ED.placeBlock((bx, by, bz), Block(bush_material))
                    placed_blocks.add((bx, by, bz))
    for bx, by, bz in placed_blocks:
        ED.placeBlock((bx, y - 1, bz), Block(garden_floor))

def place_random_bushes(ED, house_x, house_y, house_z, garden_length, house_width, num_bushes, forbidden_bush_cells, fence_door_x, fence_door_z, occupied=None):
    """
    Place random bushes in the garden, avoiding forbidden cells, the fence door, and all occupied cells.
    Inputs:
    - ED: the Editor object to place blocks in the world
    - house_x, house_y, house_z: the coordinates of the house
    - garden_length: the length of the garden area
    - house_width: the width of the house (also the width of the garden area)
    - num_bushes: the number of bushes to place
    - forbidden_bush_cells: a set of (x, z) tuples representing cells where bushes cannot be placed (e.g., paths, near the fence door)
    - fence_door_x, fence_door_z: the coordinates of the fence door to ensure bushes are not placed too close to it
    - occupied: an optional set of (x, z) tuples representing cells that are already occupied by other structures or features, to ensure bushes are not placed on top of them
    Returns:
    - updated forbidden_bush_cells set including the newly placed bushes
    - a set of all (x, z) tuples representing the cells occupied by bushes, which can be used for further checks when placing trees or other features
    """
    if occupied is None:
        occupied = set()
    all_bush_cells = set()
    for _ in range(num_bushes):
        bush_size = 1  
        bush_margin = bush_size // 2 + 1
        bush_min_x = house_x + bush_margin
        bush_max_x = house_x + garden_length - bush_margin - 1
        bush_min_z = house_z + bush_margin
        bush_max_z = house_z + house_width - bush_margin - 1
        bush_attempts = 0
        placed = False
        while bush_attempts < 200:
            bush_x = random.randint(bush_min_x, bush_max_x)
            bush_z = random.randint(bush_min_z, bush_max_z)
            bush_cells = set((bush_x + dx, bush_z + dz)
                            for dx in range(-bush_size//2, bush_size//2+1)
                            for dz in range(-bush_size//2, bush_size//2+1))
            if (
                all((bx, bz) not in forbidden_bush_cells for bx, bz in bush_cells)
                and all((bx, bz) not in occupied for bx, bz in bush_cells)
                and abs(bush_x - fence_door_x) > bush_size + 2
                and abs(bush_z - fence_door_z) > bush_size + 2
            ):
                if all((bx, bz) not in occupied for bx, bz in bush_cells):
                    bush(ED, bush_x, house_y + 1, bush_z, bush_size)
                    forbidden_bush_cells.update(bush_cells)
                    all_bush_cells.update(bush_cells)
                    placed = True
                    break
            bush_attempts += 1
        if not placed:
            continue
    return forbidden_bush_cells, all_bush_cells

def place_random_trees(ED, house_x, house_y, house_z, garden_length, house_width, num_trees, forbidden_tree_cells, fence_door_x, fence_door_z, occupied, crop_region_info=None):
    """
    Place random trees in the garden, avoiding forbidden cells and the fence door.
    Inputs:
    - ED: the Editor object to place blocks in the world
    - house_x, house_y, house_z: the coordinates of the house
    - garden_length: the length of the garden area
    - house_width: the width of the house (also the width of the garden area)
    - num_trees: the number of trees to place
    - forbidden_tree_cells: a set of (x, z) tuples representing cells where trees cannot be placed (e.g., paths, near the fence door)
    - fence_door_x, fence_door_z: the coordinates of the fence door to ensure trees are not placed too close to it
    - occupied: an optional set of (x, z) tuples representing cells that are already occupied by other structures or features, to ensure trees are not placed on top of them
    - crop_region_info: optional information about crop regions to avoid placing trees on them
    Returns:
    - updated forbidden_tree_cells set including the newly placed trees and their buffer zones
    - a set of all (x, z) tuples representing the cells occupied by trees and their buffer zones
    """
    all_tree_cells = set()
    for _ in range(num_trees):
        tree_size = random.randint(3, 5) 
        bush_radius = 1 
        min_x = house_x + bush_radius
        max_x = house_x + garden_length - bush_radius - 1
        min_z = house_z + bush_radius
        max_z = house_z + house_width - bush_radius - 1
        tree_attempts = 0
        placed = False
        while tree_attempts < 200:
            tree_x = random.randint(min_x, max_x)
            tree_z = random.randint(min_z, max_z)
            tree_cells = set((tree_x + dx, tree_z + dz)
                            for dx in range(-bush_radius, bush_radius+1)
                            for dz in range(-bush_radius, bush_radius+1))
            buffer_cells = set((tree_x + dx, tree_z + dz)
                              for dx in range(-bush_radius-1, bush_radius+2)
                              for dz in range(-bush_radius-1, bush_radius+2)) - tree_cells
            if (
                all((tx, tz) not in forbidden_tree_cells and (tx, tz) not in occupied for tx, tz in tree_cells)
                and all((bx, bz) not in forbidden_tree_cells and (bx, bz) not in occupied for bx, bz in buffer_cells)
                and abs(tree_x - fence_door_x) > bush_radius + 1
                and abs(tree_z - fence_door_z) > bush_radius + 1
            ):
                tree(ED, tree_x, house_y, tree_z, tree_size)
                forbidden_tree_cells.update(tree_cells)
                forbidden_tree_cells.update(buffer_cells)
                all_tree_cells.update(tree_cells)
                all_tree_cells.update(buffer_cells)
                placed = True
                break
            tree_attempts += 1
        if not placed:
            continue
    return forbidden_tree_cells, all_tree_cells

def fence_door_position(house_x, house_y, house_z, garden_length, house_width, main_door_x, main_door_z):
    """
    Estimate the best position for the garden fence door so that, if you draw straight lines from the main building door to the fence door,
    the garden is split into 4 rectangles, one of which contains about 40% of the area and the others about 20% each (with some randomness).
    Inputs:
    - house_x, house_y, house_z: the coordinates of the house
    - garden_length: the length of the garden area
    - house_width: the width of the house (used to determine the garden width)
    - main_door_x, main_door_z: the coordinates of the main building door
    Returns:
    - door_x, door_z: the coordinates of the fence door
    """
    forbidden_side = None
    if main_door_x == house_x - 1:
        forbidden_side = 'west'
    elif main_door_x == house_x + garden_length:
        forbidden_side = 'east'
    elif main_door_z == house_z - 1:
        forbidden_side = 'north'
    elif main_door_z == house_z + house_width:
        forbidden_side = 'south'
    all_sides = ['north', 'south', 'east', 'west']
    allowed_sides = [s for s in all_sides if s != forbidden_side]
    side = random.choice(allowed_sides)
    if side == 'north':
        door_x = random.randint(house_x + 1, house_x + garden_length - 2)
        door_z = house_z
    elif side == 'south':
        door_x = random.randint(house_x + 1, house_x + garden_length - 2)
        door_z = house_z + house_width - 1
    elif side == 'east':
        door_x = house_x + garden_length - 1
        door_z = random.randint(house_z + 1, house_z + house_width - 2)
    elif side == 'west':
        door_x = house_x
        door_z = random.randint(house_z + 1, house_z + house_width - 2)
    return door_x, door_z

def get_path_coords(main_door_x, main_door_z, fence_door_x, fence_door_z, house_x, house_z, garden_length, house_width):
    """
    Compute the set of coordinates for the path between the main door and the fence door.
    The path will be L-shaped, going first horizontally and then vertically, or vice versa, with equal probability.
    Inputs:
    - main_door_x, main_door_z: the coordinates of the main building door
    - fence_door_x, fence_door_z: the coordinates of the fence door
    - house_x, house_z: the coordinates of the house
    - garden_length: the length of the garden area
    - house_width: the width of the house (used to determine the garden width)
    Returns:
    - path_coords: a set of coordinates representing the path
    """
    gx0 = min(main_door_x, fence_door_x)
    gx1 = max(main_door_x, fence_door_x)
    gz0 = min(main_door_z, fence_door_z)
    gz1 = max(main_door_z, fence_door_z)
    if fence_door_z == gz0:
        path_front_fence = (fence_door_x, fence_door_z+1)
    elif fence_door_z == gz1:
        path_front_fence = (fence_door_x, fence_door_z-1)
    elif fence_door_x == gx0:
        path_front_fence = (fence_door_x+1, fence_door_z)
    elif fence_door_x == gx1:
        path_front_fence = (fence_door_x-1, fence_door_z)
    else:
        path_front_fence = (fence_door_x, fence_door_z)
    if main_door_x == gx0:
        path_front_main = (main_door_x+1, main_door_z)
    elif main_door_x == gx1:
        path_front_main = (main_door_x-1, main_door_z)
    elif main_door_z == gz0:
        path_front_main = (main_door_x, main_door_z+1)
    elif main_door_z == gz1:
        path_front_main = (main_door_x, main_door_z-1)
    else:
        path_front_main = (main_door_x, main_door_z)
    path_coords = set()
    x0, z0 = path_front_main
    x1, z1 = path_front_fence
    if random.choice([True, False]):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            path_coords.add((x, z0))
        for z in range(min(z0, z1), max(z0, z1) + 1):
            path_coords.add((x1, z))
    else:
        for z in range(min(z0, z1), max(z0, z1) + 1):
            path_coords.add((x0, z))
        for x in range(min(x0, x1), max(x0, x1) + 1):
            path_coords.add((x, z1))
    path_coords.add(path_front_fence)
    path_coords.add(path_front_main)
    return path_coords

def clear(house_x, house_y, house_z, house_height, house_width, house_length):
    """
    Clear the space inside the foundation and walls to make room for furniture and stairs.
    This function ensures that the interior of the house is empty by replacing any blocks within the foundation and walls with air blocks. 
    It also clears the area in front of the main door to ensure there is a clear path for entering the house.
    Inputs:
    - house_x, house_y, house_z: the coordinates of the house
    - house_height: the height of each floor of the house
    - house_width: the width of the house
    - house_length: the length of the house
    """
    x = house_x + house_length // 2
    z = house_z - 1
    for y in range(house_y, house_y + 4):
        ED.placeBlock((x, y, z), Block("minecraft:air"))
        ED.placeBlock((x, y, z-1), Block("minecraft:air"))

def solid_found(house_x, house_y, house_z, house_height, house_width, house_length):
    """
    Reinforce the base of the foundation by placing blocks under any air blocks within the foundation area. This ensures that the foundation is solid and can support the structure above it.
    The function iterates through the area defined by the house dimensions and checks for any air blocks at the level of the foundation. If it finds an air block, it places a grass block underneath it to provide support.
    Additionally, it ensures that the area in front of the main door is also reinforced to prevent any potential issues with the entrance of the house.
    Inputs:
    - house_x, house_y, house_z: the coordinates of the house
    - house_height: the height of each floor of the house
    - house_width: the width of the house
    - house_length: the length of the house
    """
    for x in range(house_x, house_x + house_length + 1):
        for z in range(house_z, house_z + house_width + 1):
            if ED.getBlock((x, house_y - 1, z)) == Block("minecraft:air"):
                ED.placeBlock((x, house_y - 1, z), Block("minecraft:grass_block"))

def build_door(ED, house_x, house_y, house_z, house_height, house_width, house_length, starting_x=None):
    """
    Place a door at the given coordinates. If starting_x is provided, place a stair block for the main entrance. The function ensures that the door is properly placed and that there is a clear path in front of it.
    Inputs:
    - ED: the Editor object to place blocks in the world
    - house_x, house_y, house_z: the coordinates of the door
    - house_height: the height of each floor of the house (used to determine the height of the door)
    - house_width: the width of the house (used to determine the position of the door)
    - house_length: the length of the house (used to determine the position of the door)
    - starting_x: optional x coordinate to determine if this is the main entrance, if provided, a stair block will be placed in front of the door to ensure a smooth entrance
    """
    door_material = material("door")
    x, y, z = house_x, house_y, house_z
    door_height = 2
    for dy in range(door_height):
        ED.placeBlock((x, y + dy, z), Block("minecraft:air"))
    ED.placeBlock((x, y, z), Block(door_material, {"hinge": "left", "half": "lower"}))
    if door_height > 1:
        ED.placeBlock((x, y + 1, z), Block(door_material, {"hinge": "left", "half": "upper"}))
    if starting_x is not None and house_x == starting_x:
        support_block = ED.getBlock((x - 1, y - 1, z))
        if str(support_block) == "minecraft:air":
            ED.placeBlock((x - 1, y - 1, z), Block("minecraft:grass_block"))


def build_garden_fence(ED, x, y, z, length, width):
    """
    Build a fence around the garden area defined by the given coordinates and dimensions. The fence will be placed one block above the ground level (y + 1) and will surround the entire perimeter of the garden.
    The function ensures that the fence is properly placed along the edges of the garden and that it does not interfere with the main building or any other structures. It also takes into account the dimensions of
    the garden to ensure that the fence is correctly aligned and provides a clear boundary for the garden area.
    Inputs:
    - ED: the Editor object to place blocks in the world
    - x, y, z: the coordinates of the starting point of the garden (the corner closest to the house)
    - length: the length of the garden area    
    - width: the width of the garden area
    """
    fence_material = material("fence")
    for fx in range(x, x + length):
        ED.placeBlock((fx, y + 1, z), Block(fence_material)) 
        ED.placeBlock((fx, y + 1, z + width - 1), Block(fence_material))
    for fz in range(z, z + width):
        ED.placeBlock((x, y + 1, fz), Block(fence_material))

def build_garden_floor(ED, x, y, z, length, width):
    """
    Build the garden floor by placing blocks of garden floor material across the entire area defined by the given coordinates and dimensions. 
    The garden floor will be placed at the specified y level, covering the ground of the garden area.
    The function ensures that the garden floor is properly placed and covers the entire area of the garden, providing a solid surface for the garden. 
    It also takes into account the dimensions of the garden to ensure that the floor is correctly aligned and provides a consistent base for any plants, 
    paths, or other features that may be added to the garden.
    Inputs:
    - ED: the Editor object to place blocks in the world
    - x, y, z: the coordinates of the starting point of the garden (the corner closest to the house)
    - length: the length of the garden area
    - width: the width of the garden area
    """
    floor_material = material("garden_floor")
    for gx in range(x, x + length):
        for gz in range(z, z + width):
            ED.placeBlock((gx, y, gz), Block(floor_material))

def build_garden_path(ED, main_door_x, main_door_z, fence_door_x, fence_door_z, y, x=None, z=None, length=None, width=None, path_material=None):
    """
    Create a path between the main building door and the garden fence door, following the rectangles split logic (L-shaped path).
    The path will be created by placing blocks of the specified path material along the coordinates determined by the get_path_coords function, which calculates the optimal path between the two doors.
    The function ensures that the path is properly placed and provides a clear route from the main building door to the garden fence door, allowing for easy access to the garden area. It also takes into
    account the dimensions of the garden to ensure that the path is correctly aligned and does not interfere with any other features or structures in the garden.
    Inputs:
    - ED: the Editor object to place blocks in the world
    - main_door_x, main_door_z: the coordinates of the main building door
    - fence_door_x, fence_door_z: the coordinates of the garden fence door
    - y: the y level at which to place the path blocks
    - x, z, length, width: optional parameters to determine the garden area for path alignment, if not provided, the function will still create a path between the two doors but may not be perfectly aligned with the garden layout
    - path_material: optional material for the path blocks, if not provided, a default material will be used for the path
    """
    path_material = "minecraft:gravel"
    path_coords = get_path_coords(main_door_x, main_door_z, fence_door_x, fence_door_z, x, z, length, width)
    for (px, pz) in path_coords:
        ED.placeBlock((px, y, pz), Block(path_material))
    ED.placeBlock((fence_door_x, y, fence_door_z), Block(path_material))

def build_garden_fence_door(ED, x, y, z, length, width, door_x=None, door_z=None):
    """
    Place a door in the garden fence at the specified coordinates. If door_x and door_z are provided, the door will be placed at those coordinates; otherwise, a random position along the fence will be chosen for the door.
    The function ensures that the door is properly placed within the fence and that it provides a clear entry point to the garden area. It also takes into account the dimensions of the garden and the position
    of the main building door to ensure that the fence door is optimally located for easy access to the garden while maintaining the overall aesthetic and functionality of the garden layout.
    Inputs:
    - ED: the Editor object to place blocks in the world
    - x, y, z: the coordinates of the starting point of the garden (the corner closest to the house)
    - length: the length of the garden area
    - width: the width of the garden area
    - door_x, door_z: optional coordinates for the fence door, if not provided, a random position along the fence will be chosen for the door
    """
    gate_material = material("door_fence")
    if door_x is None:
        fence_x = random.randint(x + 1, x + length - 2)
    else:
        fence_x = door_x
    if door_z is None:
        fence_z = z
    else:
        fence_z = door_z
    if fence_z == z:
        facing = "south"
    elif fence_z == z + width - 1:
        facing = "north"
    elif fence_x == x:
        facing = "east"
    elif fence_x == x + length - 1:
        facing = "west" 
    else:
        facing = "south" 
    ED.placeBlock((fence_x, y + 1, fence_z), Block(gate_material, {"facing": facing}))
    ED.placeBlock((fence_x, y + 2, fence_z), Block("minecraft:air"))

def build_garden_lights(ED, garden_x, garden_y, garden_z, garden_length, garden_width):
    """
    Place lanterns on top of the fence at each garden corner. The lanterns will be placed at the coordinates corresponding to the corners of the garden, which are determined by the starting coordinates and the dimensions of the garden.
    The function ensures that the lanterns are properly placed and provide illumination for the garden area, enhancing the aesthetic appeal and functionality of the garden, especially during nighttime. It also takes into account the
    layout of the garden to ensure that the lanterns are positioned in a way that complements the overall design and provides balanced lighting throughout the garden space.
    Inputs:
    - ED: the Editor object to place blocks in the world
    - garden_x, garden_y, garden_z: the coordinates of the starting point of the garden (the corner closest to the house)
    - garden_length: the length of the garden area
    - garden_width: the width of the garden area
    """
    lantern_block = material("light")
    corners = [
        (garden_x, garden_z),
        (garden_x + garden_length - 1, garden_z),
        (garden_x, garden_z + garden_width - 1),
        (garden_x + garden_length - 1, garden_z + garden_width - 1)
    ]
    for (x, z) in corners:
        ED.placeBlock((x, garden_y + 2, z), Block(lantern_block))

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

