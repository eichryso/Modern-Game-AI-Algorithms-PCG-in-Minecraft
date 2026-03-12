import logging
import numpy as np

from gdpc import Editor

from inventory import material
from exterior_main import build_garden_room 

WALL_MATERIAL = material("wall")
ROOF_MATERIAL = material("roof")

def main(same_size=False):
    """
    Main function to build the garden area with trees and bushes, ensuring that they are placed in suitable locations based on the terrain and avoiding water and steep slopes.
    The function scans the building area for suitable locations to place garden rooms, and for each valid location, it builds a garden room and populates it with trees and bushes while respecting the constraints of
    the garden area and the presence of the fence door. We do not use the scan_terrain function as we test on a flat world. Default garden sizes are random, but the user can choose to use fixed sizes for all gardens by passing the 
    --same_size flag when running the script.
    """
    logging.basicConfig(format="%(name)s - %(levelname)s - %(message)s")
    ED = Editor(buffering=True)
    
    building_area = ED.getBuildArea() 
    world_slice = ED.loadWorldSlice(building_area.toRect(), cache=True)
    house_height = 5
    min_garden = 4
    max_garden = 20
    heightmap = world_slice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]
    x1, y1, z1 = building_area.begin
    x2, y2, z2 = building_area.last
    build_length = abs(x1 - x2)
    build_width = abs(z1 - z2)
    start_x = min(x1, x2)
    start_z = min(z1, z2)
    occupancy = np.zeros((build_length, build_width), dtype=bool)
    fixed_garden_length = 10
    fixed_garden_width = 20
    grid_x = 0
    while grid_x < build_length - min_garden:
        grid_z = 0
        while grid_z < build_width - min_garden:
            if same_size:
                garden_length = min(fixed_garden_length, build_length - grid_x)
                garden_width = min(fixed_garden_width, build_width - grid_z)
            else:
                garden_length = np.random.randint(min_garden, min(max_garden, build_length - grid_x) + 1)
                garden_width = np.random.randint(min_garden, min(max_garden, build_width - grid_z) + 1)
            occ_slice = occupancy[grid_x:grid_x+garden_length+1, grid_z:grid_z+garden_width+1]
            if np.any(occ_slice):
                grid_z += 1
                continue
            subgrid = heightmap[grid_x:grid_x+garden_length, grid_z:grid_z+garden_width]
            avg_height = np.mean(subgrid)
            diff = np.abs(subgrid - avg_height)
            avg_diff = np.mean(diff)
            if avg_diff > 1.5:
                grid_z += 1
                continue
            has_water = False
            for i in range(garden_length):
                for j in range(garden_width):
                    y_ij = int(heightmap[grid_x+i, grid_z+j])
                    block_str = ED.getBlock((start_x + grid_x + i, y_ij-1, start_z + grid_z + j)).__str__()
                    if "minecraft:water" in block_str:
                        has_water = True
                        break
                if has_water:
                    break
            if has_water:
                grid_z += 1
                continue
            garden_x = start_x + grid_x
            garden_z = start_z + grid_z
            garden_y = int(np.round(avg_height))
            build_garden_room(ED, garden_x, garden_y, garden_z, garden_length, garden_width, house_height)
            occupancy[grid_x:grid_x+garden_length+1, grid_z:grid_z+garden_width+1] = True
            grid_z += garden_width + 1
        grid_x += garden_length + 1

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Showcase exterior garden generation.")
    parser.add_argument('--same_size', action='store_true', help='Use fixed size for all gardens (default: random sizes)')
    args = parser.parse_args()
    try:
        main(same_size=args.same_size)
    except KeyboardInterrupt:
        pass
