import random
from foundation.inventory import material
from gdpc import Block

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
