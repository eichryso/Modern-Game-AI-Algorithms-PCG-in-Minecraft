import random
from foundation.inventory import material
from gdpc import Block, Editor


FLOOR_MATERIAL = material("foundation")
WALL_MATERIAL = material("wall")
ROOF_MATERIAL = material("roof")


ED = Editor(buffering=True)

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
    from exterior_structures.helpers import get_path_coords
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

