from gdpc import Block

from inventory import material
from foundation_structures import build_foundation, build_walls, build_stairs, build_windows
from exterior_structures import build_door, clear, solid_found
from interior_main import build_furniture

FLOOR_MATERIAL = material("foundation")
WALL_MATERIAL = material("wall")

def build_floor(ED, dims, floor_y, house_height, num_floors, floor, stair_x, stair_z, stair_positions, wall_material=None, showcase_foundation=False, floor_material=None):
    """
    Build a single floor, including stairs, windows, walls, foundation, and furniture, and always preserve stairs and fill all floor area.
    If floor == 0, build the foundation and walls for the first floor, and place the main door and garden door.
    If floor > 0, build the foundation for the upper floor, and build walls for the upper floor. The foundation for the upper floor will be built with an opening for the stairs,
    and the walls will be built with an opening for the stairs if the stairs are within the floor area. Furniture will be added to all floors, but on upper floors it will avoid blocking the stairs.
    If showcase is True, only build the foundation and walls, without adding furniture or stairs, to showcase only the foundation of the house.
    Inputs:
    - ED: the Editor object to place blocks in the world
    - dims: a dictionary containing the dimensions of the house, with keys 'x', 'z', 'width', and 'length'
    - floor_y: the y-coordinate of the floor to build
    - house_height: the height of each floor of the house
    - num_floors: the total number of floors in the house
    - floor: the index of the floor to build (0 for the first floor, 1 for the second floor, etc.)
    - stair_x, stair_z: the x and z coordinates of the stairs, if they exist (None if no stairs)
    - stair_positions: a dictionary to store the positions of stairs for each floor, used to create openings in the foundation and walls
    - wall_material: optional material for the walls (defaults to WALL_MATERIAL)
    - floor_material: optional material for the floor (defaults to FLOOR_MATERIAL)
    - showcase_foundation: if True, only build the foundation and walls without furniture or stairs, to showcase the foundation
    """
    if floor_material is None:
        floor_material = FLOOR_MATERIAL
    if wall_material is None:
        wall_material = WALL_MATERIAL

    x, z, width, length = dims['x'], dims['z'], dims['width'], dims['length']
    if floor == 0:
        build_foundation(ED, Block, x, floor_y, z, length, width, material=floor_material)
        build_walls(ED, Block, x, floor_y, z, house_height, width, length, material=wall_material)
        solid_found(x, floor_y, z, house_height, width, length)
        clear(x, floor_y, z, house_height, width, length)
        stair_positions['prev_dims'] = dims
        main_door_x = x
        main_door_z = z + width // 2
        build_door(ED, main_door_x, floor_y + 1, main_door_z, house_height, width, length)
        garden_door_x = x + length - 1
        garden_door_z = z + width // 2
        build_door(ED, garden_door_x, floor_y + 1, garden_door_z, house_height, width, length)
    else:
        build_foundation(
            ED, Block, x, None, z, length, width, material=floor_material,
            upper_floor=True, stair_positions=stair_positions, floor=floor, house_height=house_height, floor_y=floor_y
        )
        build_walls(ED, Block, x, floor_y, z, house_height, width, length, material=wall_material)
        stair_positions['prev_dims'] = dims
    print(f"Finished building foundation and walls for floor {floor + 1}.")
    build_windows(ED, x, floor_y, z, house_height, width, length)
    if showcase_foundation == False:
        blocked_positions = set()
        if floor == 0:
            door_z = z + width // 2
            blocked_positions.add((x, door_z))
            blocked_positions.add((x + 1, door_z))
            garden_door_x = x + length - 1
            garden_door_z = z + width // 2
            blocked_positions.add((garden_door_x, garden_door_z))
            blocked_positions.add((garden_door_x + 1, garden_door_z))
        if stair_x is not None and stair_z is not None:
            for dx in range(-1, 2):
                for dz in range(-1, 2):
                    blocked_positions.add((stair_x + dx, stair_z + dz))
            blocked_positions.add((stair_x, stair_z + house_height))
        is_top_floor = (floor == num_floors - 1)
        try:
            build_furniture(ED, dims, floor_y, house_height, blocked_positions=blocked_positions, is_top_floor=is_top_floor)
        except TypeError:
            build_furniture(ED, dims, floor_y, house_height)
        print(f"Finished building furniture for floor {floor + 1}.")
        
        if stair_x is not None and stair_z is not None:
            stair_positions[floor] = (stair_x, stair_z)
            if (x <= stair_x < x+length and z <= stair_z < z+width):
                build_stairs(ED, x, floor_y, z, house_height, width, length, stair_x, stair_z)
                print(f"Finished building stairs for floor {floor + 1}.")
    else:
        pass
