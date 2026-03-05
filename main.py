import logging
import numpy as np

from gdpc import Block, Editor

from terrain_scan import scan_terrain
from foundation.inventory import material
from foundation.structure import build_roof
from foundation.helpers import multi_floor_dimensions, stair_position
from foundation.found_main import build_floor

from exterior_structures.ext_main import build_garden_room 


WALL_MATERIAL = material("wall")
ROOF_MATERIAL = material("roof")


def main():
    """
    Main function to generate a multi-floor house with interior furniture and exterior garden room. 
    The function first scans the terrain to find a suitable location for the house, then determines the dimensions and number of floors.
    It then builds each floor of the house, including the foundation, walls, windows, and furniture, while ensuring that stairs and openings are preserved. 
    Finally, it builds the roof and the garden room.
    """
    logging.basicConfig(format="%(name)s - %(levelname)s - %(message)s")
    ED = Editor(buffering=True)
    
    building_area = ED.getBuildArea() 
    world_slice = ED.loadWorldSlice(building_area.toRect(), cache=True)

    house_height = np.random.randint(5, 6)
    house_width = np.random.randint(20, 25)
    house_length = np.random.randint(30, 35)
    num_floors = np.random.randint(2, 5)

    min_main_length = 15
    min_garden_length = 4
    main_length = np.random.randint(min_main_length, house_length - min_garden_length + 1)
    garden_length = house_length - main_length
    print("Generating house...")
    print(f"House dimensions: length = {house_length} and width = {house_width}")
    heightmap = world_slice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]
    house_x, house_y, house_z, decision = scan_terrain(ED, building_area, heightmap, house_width, house_length)
    if decision:
        print(f"Suitable location found at ({house_x}, {house_y}, {house_z}). Building house...")
        ROOF_MATERIAL = material("roof")
        roof_material = ROOF_MATERIAL
        floor_dims = multi_floor_dimensions(house_x + garden_length, house_z, main_length, house_width, num_floors)
        print(f"Initial requested number of floors: {num_floors}")
        print(f"Final generated number of floors: {len(floor_dims)}")
        stair_positions = {}
        wall_material = material("wall")
        for floor in range(len(floor_dims)):
            floor_y = house_y + floor * house_height
            dims = floor_dims[floor]
            stair_x, stair_z = stair_position(floor_dims, floor, stair_positions)
            print(f"Building floor {floor + 1} at y={floor_y} with dimensions: {dims}")
            build_floor(ED, dims, floor_y, house_height, num_floors, floor, stair_x, stair_z, stair_positions, wall_material=wall_material)
        top_floor = len(floor_dims) - 1
        floor_y = house_y + top_floor * house_height
        dims = floor_dims[top_floor]
        for fx in range(dims['x'], dims['x'] + dims['length']):
            for fz in range(dims['z'], dims['z'] + dims['width']):
                ED.placeBlock((fx, floor_y + house_height, fz), Block(wall_material))
        print("Building roof...")
        build_roof(ED, Block, dims['x'], floor_y+1, dims['z'], house_height, dims['width'], dims['length'], material=roof_material)
        print("Building garden room...")    
        build_garden_room(ED, house_x, house_y, house_z, garden_length, house_width, house_height)
        print("House generation complete.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
