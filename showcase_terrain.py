import logging
import numpy as np
import matplotlib.pyplot as plt
import os

from gdpc import Editor
from terrain_scan import  scan_terrain_showcase

def main():
    """
    Main function to scan the terrain in the building area and visualize the suitability of different locations for building the house. 
    The function loads the heightmap of the building area, identifies suitable locations for building the house based on the terrain, 
    and visualizes the heightmap with overlays indicating the best, median, and worst locations for building the house. 
    The function also identifies and marks water blocks in the terrain to provide additional context for the suitability of different locations.
    We save the resulting plot as an image file in the 'image' directory, with a filename provided by the user. 
    """
    logging.basicConfig(format="%(name)s - %(levelname)s - %(message)s")
    ED = Editor(buffering=True)
    building_area = ED.getBuildArea() 
    world_slice = ED.loadWorldSlice(building_area.toRect(), cache=True)
    house_width = np.random.randint(20, 25)
    house_length = np.random.randint(30, 35)
    heightmap = world_slice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]
    all_candidates = scan_terrain_showcase(ED, building_area, heightmap, house_width, house_length)
    n = len(all_candidates)
    best = all_candidates[0]
    median_idx = n // 2
    median = all_candidates[median_idx]
    worst = all_candidates[-1]

    plt.figure(figsize=(10, 8))
    plt.imshow(heightmap.T, origin='lower', cmap='terrain')
    plt.colorbar(label='Y Level')
    x1, y1, z1 = building_area.begin
    x2, y2, z2 = building_area.last
    build_length = abs(x1 - x2)
    build_width = abs(z1 - z2)
    water_xs = []
    water_zs = []
    for x in range(build_length):
        for z in range(build_width):
            y_ij = int(heightmap[x, z])
            block_below = ED.getBlock((x1 + x, y_ij - 1, z1 + z))
            if "minecraft:water" in str(block_below):
                water_xs.append(x)
                water_zs.append(z)
    if water_xs:
        plt.scatter(water_xs, water_zs, color='blue', marker='x', s=40, label='Water blocks')
        plt.legend()
    def overlay_rect(candidate, idx, label, color):
        avg_diff, x, y, z, subgrid = candidate
        rect = plt.Rectangle((x, z), house_length, house_width, linewidth=2, edgecolor=color, facecolor='none')
        plt.gca().add_patch(rect)
        cx = x + house_length / 2
        cz = z + house_width / 2
        plt.text(cx, cz, f'{label}\nscore={avg_diff:.2f}\n#{idx+1}', color="black", ha='center', va='center', fontsize=12, weight='bold')
    overlay_rect(best, 0, 'Best', 'green')
    overlay_rect(median, median_idx, 'Median', 'orange')
    overlay_rect(worst, n-1, 'Worst', 'red')
    plt.xlabel('X')
    plt.ylabel('Z')

    filename = input('Enter a name for the terrain plot image (without extension): ')
    outdir = os.path.join('image')
    os.makedirs(outdir, exist_ok=True)
    outpath = os.path.join(outdir, f'{filename}.png')
    plt.savefig(outpath)
    print(f'Plot saved to {outpath}')


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
