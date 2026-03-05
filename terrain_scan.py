import logging
from random import randint
import numpy as np

from gdpc import Block, Editor
from gdpc import geometry as geo
from gdpc import minecraft_tools as mt
from gdpc import editor_tools as et


logging.basicConfig(format="%(name)s - %(levelname)s - %(message)s")

def scan_terrain(ED, building_area, heightmap, housewidth, houselength):
    """
    Scan the terrain within the building area to find a suitable location for placing a house of given width and length. The function iterates over possible subgrids of the heightmap corresponding to the
    house dimensions, checks for flatness and absence of water blocks, and returns the coordinates of the flattest valid subgrid along with a decision boolean indicating whether a suitable location was found.
    Inputs:
    - ED: the Editor object to access block information
    - building_area: the area within which to scan for a suitable location
    - heightmap: the heightmap of the terrain
    - housewidth: the width of the house
    - houselength: the length of the house
    Returns:
    - x, y, z: the coordinates of the flattest valid subgrid for placing the house
    - decision: a boolean indicating whether a suitable location was found
    """
    x1, y1, z1 = building_area.begin
    x2, y2, z2 = building_area.last
    build_length = abs(x1 - x2)
    build_width = abs(z1 - z2)
    starting_x, starting_y, starting_z = x1, y1, z1
    min_diff = np.inf
    max_diff = 0
    flattest_subgrid = None
    counter = 0
    valid_counter = 0
    x1, y1, z1 = building_area.begin
    x2, y2, z2 = building_area.last
    flattest_subgrid_x, flattest_subgrid_y, flattest_subgrid_z = 0, 0, 0
    build_length = abs(x1 - x2)
    build_width = abs(z1 - z2)
    for x in range(0, build_length - houselength):
        for z in range(0, build_width - housewidth):
            subgrid = np.zeros((houselength, housewidth))
            subgrid_valid = True
            for i in range(houselength):
                for j in range(housewidth):
                    subgrid[i,j] = heightmap[x+i,z+j]
                    y_ij = int(heightmap[x+i,z+j])
                    if "minecraft:water" in ED.getBlock((starting_x+ x + i, y_ij-1, starting_z+ z + j)).__str__():
                        subgrid_valid = False
                        break
                if subgrid_valid == False:
                    break
            counter += 1
            if subgrid_valid == False:
                continue
            else:
                valid_counter += 1

                avg_height = np.mean(subgrid)
                diff = np.abs(subgrid - avg_height)

                avg_diff = np.mean(diff)

                if avg_diff < min_diff:
                    min_diff = avg_diff
                    flattest_subgrid = subgrid
                    flattest_subgrid_x = x
                    flattest_subgrid_y = int(np.mean(subgrid))
                    flattest_subgrid_z = z

                if avg_diff > max_diff:
                    max_diff = avg_diff

    if flattest_subgrid is not None:
        decision = True
    else:
        decision = False
    return flattest_subgrid_x + x1, flattest_subgrid_y, flattest_subgrid_z + z1, decision

def scan_terrain_showcase(ED, building_area, heightmap, housewidth, houselength):
    """
    Scan the terrain and return diagnostics for all the subgrids. This function is similar to scan_terrain but instead of returning just the flattest valid subgrid, 
    it collects information about all valid subgrids andsorts them by flatness.
    Inputs:
    - ED: the Editor object to access block information
    - building_area: the area within which to scan for suitable locations
    - heightmap: the heightmap of the terrain
    - housewidth: the width of the house
    - houselength: the length of the house
    """
    x1, y1, z1 = building_area.begin
    x2, y2, z2 = building_area.last
    build_length = abs(x1 - x2)
    build_width = abs(z1 - z2)
    starting_x, starting_y, starting_z = x1, y1, z1
    subgrid_infos = []
    for x in range(0, build_length - houselength):
        for z in range(0, build_width - housewidth):
            subgrid = np.zeros((houselength, housewidth))
            subgrid_valid = True
            for i in range(houselength):
                for j in range(housewidth):
                    subgrid[i,j] = heightmap[x+i,z+j]
                    y_ij = int(heightmap[x+i,z+j])
                    if "minecraft:water" in ED.getBlock((starting_x+ x + i, y_ij-1, starting_z+ z + j)).__str__():
                        subgrid_valid = False
                        break
                if not subgrid_valid:
                    break
            if not subgrid_valid:
                continue
            avg_height = np.mean(subgrid)
            diff = np.abs(subgrid - avg_height)
            avg_diff = np.mean(diff)
            subgrid_infos.append((avg_diff, x, int(avg_height), z, subgrid.copy()))
    subgrid_infos.sort(key=lambda tup: tup[0])
    return subgrid_infos 

def main():
    try:
        pass
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()


