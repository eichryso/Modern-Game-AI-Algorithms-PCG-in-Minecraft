import logging
import numpy as np

from gdpc import Editor

from foundation.inventory import material
from foundation.helpers import multi_floor_dimensions, stair_position
from foundation.found_main import build_floor
from exterior_structures.ext_main import build_garden_room 


WALL_MATERIAL = material("wall")
ROOF_MATERIAL = material("roof")


def main():
    """
    Main function to showcase the interior of the house by building only the foundation and walls for each floor, adding furniture and stairs. The function scans the building area for suitable locations to place the house, 
    and for each valid location, it builds the foundation and walls for each floor of the house, as well as the roof, while respecting the constraints of the building area. We build only the interior furniture and stairs of
    the first floor. We do not use the scan_terrain function as we test on a flat world. 
    """
    logging.basicConfig(format="%(name)s - %(levelname)s - %(message)s")
    ED = Editor(buffering=True)
    building_area = ED.getBuildArea() 
    world_slice = ED.loadWorldSlice(building_area.toRect(), cache=True)
    house_height = 5
    house_width = 20
    house_length = 30
    num_floors = 3
    main_length = 20
    garden_length = house_length - main_length
    heightmap = world_slice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]
    x1, y1, z1 = building_area.begin
    x2, y2, z2 = building_area.last
    build_length = abs(x1 - x2)
    build_width = abs(z1 - z2)
    start_x = min(x1, x2)
    start_z = min(z1, z2)
    occupancy = np.zeros((build_length, build_width), dtype=bool)
    for grid_x in range(0, build_length - house_length, house_length + 1):
        for grid_z in range(0, build_width - house_width, house_width + 1):
            if np.any(occupancy[grid_x:grid_x+house_length+1, grid_z:grid_z+house_width+1]):
                continue
            subgrid = heightmap[grid_x:grid_x+house_length, grid_z:grid_z+house_width]
            avg_height = np.mean(subgrid)
            diff = np.abs(subgrid - avg_height)
            avg_diff = np.mean(diff)
            if avg_diff > 1.5:
                continue
            has_water = False
            for i in range(house_length):
                for j in range(house_width):
                    y_ij = int(heightmap[grid_x+i, grid_z+j])
                    block_str = ED.getBlock((start_x + grid_x + i, y_ij-1, start_z + grid_z + j)).__str__()
                    if "minecraft:water" in block_str:
                        has_water = True
                        break
                if has_water:
                    break
            if has_water:
                continue
            house_x = start_x + grid_x
            house_z = start_z + grid_z
            house_y = int(np.round(avg_height))
            floor_material = material("foundation")
            floor_dims = multi_floor_dimensions(house_x + garden_length, house_z, main_length, house_width, num_floors)
            stair_positions = {}
            wall_material = material("wall")
            floor = 0
            floor_y = house_y + floor * house_height
            dims = floor_dims[floor]
            stair_x, stair_z = stair_position(floor_dims, floor, stair_positions)
            build_floor(ED, dims, floor_y, house_height, num_floors, floor, stair_x, stair_z, stair_positions, wall_material=wall_material, floor_material=floor_material)
            build_garden_room(ED, house_x, house_y, house_z, garden_length, house_width, house_height, showcase_foundation=True)
            occupancy[grid_x:grid_x+house_length+1, grid_z:grid_z+house_width+1] = True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
