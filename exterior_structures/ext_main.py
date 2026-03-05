import random
from gdpc import Block
from exterior_structures.helpers import fence_door_position, get_path_coords, build_garden_floor, build_garden_fence, build_garden_fence_door, build_garden_path, build_garden_lights
from exterior_structures.tree_and_bushes import place_random_bushes, place_random_trees
from exterior_structures.extra import place_random_crop_region_full, place_garden_flowers, place_random_pond


def build_garden_room(ED, house_x, house_y, house_z, garden_length, house_width, house_height, showcase_foundation=False):
    """
    Build the garden room, including clearing the area, placing the floor, fence, doors, path, crops, pond, trees, bushes, and flowers. 
    The function first clears the area for the garden, then builds the garden floor. If showcase_foundation is False, it proceeds to build the fence, fence door, and path from the main door to the fence door.
    It then randomly places a pond and a crop region in the garden, ensuring they do not overlap with the path or each other.
    Finally, it places random trees and bushes in the remaining available space, and fills in flowers in any remaining non-occupied spots.
    Inputs:
    - ED: the Editor object to place blocks in the world
    - house_x, house_y, house_z: the coordinates of the house, which also serve as the corner of the garden
    - garden_length: the length of the garden area extending from the house
    - house_width: the width of the house, which also defines the width of the garden area
    - house_height: the height of the house, used to ensure trees and bushes do not exceed the height of the house
    - showcase_foundation: if True, only build the foundation and fence without adding the path, crops, pond, trees, bushes, or flowers, to showcase only the foundation
    """
    for x in range(house_x, house_x + garden_length):
        for z in range(house_z, house_z + house_width):
            for y in range(house_y + 1, house_y + house_height):
                ED.placeBlock((x, y, z), Block("minecraft:air"))
    build_garden_floor(ED, house_x, house_y, house_z, garden_length, house_width)
    if showcase_foundation == False:
        main_door_x = house_x + garden_length
        main_door_z = house_z + house_width // 2
        fence_door_x, fence_door_z = fence_door_position(
            house_x, house_y, house_z, garden_length, house_width, main_door_x, main_door_z
        )
        path_coords = get_path_coords(main_door_x, main_door_z, fence_door_x, fence_door_z, house_x, house_z, garden_length, house_width)
        build_garden_fence(ED, house_x, house_y, house_z, garden_length, house_width)
        build_garden_fence_door(ED, house_x, house_y, house_z, garden_length, house_width, fence_door_x, fence_door_z)
        build_garden_lights(ED, house_x, house_y, house_z, garden_length, house_width)
        occupied = set(path_coords)
        occupied.update((x, house_z) for x in range(house_x, house_x + garden_length))
        occupied.update((x, house_z + house_width - 1) for x in range(house_x, house_x + garden_length))
        occupied.update((house_x, z) for z in range(house_z, house_z + house_width))
        # Always keep path_coords in occupied for all placements
        occupied |= set(path_coords)
        pond_cells = place_random_pond(ED, house_x, house_y, house_z, garden_length, house_width, occupied)
        if pond_cells:
            occupied.update(pond_cells)
            pond_positions = pond_cells
        else:
            pond_positions = set()
        occupied |= set(path_coords)
        crop_result = place_random_crop_region_full(ED, house_x, house_y, house_z, garden_length, house_width, occupied)
        crop_region = False
        crop_positions = set()
        crop_x0 = crop_z0 = crop_w = crop_h = None
        if crop_result:
            crop_region, crop_positions, crop_x0, crop_z0, crop_w, crop_h, crop, floor = crop_result
            occupied.update(crop_positions)
        forbidden_tree_cells = occupied | pond_positions
        if crop_region:
            crop_area = set((x, z) for x in range(crop_x0, crop_x0+crop_w) for z in range(crop_z0, crop_z0+crop_h))
            forbidden_tree_cells |= crop_area
        forbidden_tree_cells |= set(path_coords)
        num_trees = random.randint(3, 6)
        forbidden_tree_cells, tree_cells = place_random_trees(ED, house_x, house_y, house_z, garden_length, house_width, num_trees, forbidden_tree_cells, fence_door_x, fence_door_z, occupied, crop_result)
        forbidden_bush_cells = forbidden_tree_cells.copy()
        num_bushes = random.randint(1, 2)
        forbidden_bush_cells |= set(path_coords)
        forbidden_bush_cells, bush_cells = place_random_bushes(ED, house_x, house_y, house_z, garden_length, house_width, num_bushes, forbidden_bush_cells, fence_door_x, fence_door_z, occupied)
        occupied.update(bush_cells)
        occupied |= set(path_coords)
        place_garden_flowers(ED, house_x, house_y, house_z, garden_length, house_width, occupied)
        build_garden_path(ED, main_door_x, main_door_z, fence_door_x, fence_door_z, house_y, house_x, house_z, garden_length, house_width)
    else:
        pass

