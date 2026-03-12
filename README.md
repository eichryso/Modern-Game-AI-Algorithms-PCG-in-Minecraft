# Modern Game AI in Algortihms: Assignment 1

Eirini Chrysovergi, s3972453, Master in Astronomy and Research

In this repository we provide the nescessary source code for the first assignment of the course Modern Game AI in Algortihms. Our task is to apply Procedural Content Generation (PCG) to generate a house in Minecraft.


## Instructions

In order to run the code the following software need to be installed:

- Python
- Numpy
- Matplotlib
- Minecraft 1.19.2 (Java Edition)
- GGDMC HTTP interface mod (v1.8.1)
- GDPC Python package

In principal our algorithm is able to adapt to the possibilities of the RNGesus of the Minecraft world. Therefore, we can create a random Minecraft world with the fabric mode installed. In the Minecraft chat (press t) run the following command:

```bash
/buildarea set ~ ~ ~ ~100 ~ ~100
```

Clone this repository and run in the terminal:

```bash
python3 -m main 
```

Depending on the hardware this may take some time (usually less than a minute). When completed, the generated house should be properly placed in our build area.

Some examples of generated houses in different random worlds:

![ex1](/image/showcase_flat_world.png)
![ex2](/image/showcase_amplified_world.png)
![ex3](/image/showcase_large_biomes_1.png)
![ex4](/image/showcase_large_biomes_2.png)

## Showcase

The source code showcasing the adaptation to the terrain, our foundation as well as the interior and exterior decoration are included in:

- showcase_terrain.py
- showcase_fouundation.py
- showcase_interior.py
- showcase_exterior.py

These files can be run in the terminal after we have defined the building area by typing in the Minecraft chat:
```bash
/buildarea set ~ ~ ~ ~100 ~ ~100
```

### Showcase Terrain
We can test the adaptability of our algorithm to the terrain of the world by running in the terminal:

```bash
python3 -m showcase_terrain
```

The code scans the world slice and produces a plot of the x-z plane colormapped by the y level. On top, we overlay three candidate regions of varying flatness score to indicate the best, median and worst possible placement for our building. This code can be tested in a totally random world with random building area sizes. When running, the algorithm prompts to pass an appropriate name for saving the figures in the ./image folder. 

Some examples showcasing the terrain evaluation:

![terrain_ex1](/image/terrain_test_1.png)
![terrain_ex2](/image/terrain_test_2.png)
![terrain_ex3](/image/terrain_test_3.png)
![terrain_ex4](/image/terrain_test_4.png)

### Showcase Foundation

For the foundation of the building we can run in the terminal:
```bash
python3 -m showcase_foundation
```

The code generates  similar sized houses, tightly packed together in the build area region. In order to visualize only the foundation of our houses, we generate only the floors, walls, floors and windows of our buildings. Some generated examples can be seen in the ./image folder. 

Some examples showcasing the foundation of our buildings:

![found_ex1](/image/foundation_showcase_1.png)
![found_ex2](/image/foundation_showcase_2.png)

### Showcase Interior

Similarly, we can visualize the interior structures generated in our house. We can visualize it in a defined building area by running:

```bash
python3 -m showcase_interior
```

With this code we produce similar sized, tightly packed houses in our build area reagion. In order to visualize only the interior, we generate only the ground floors for our houses. Some generated examples can be seem in the ./image folder. 

Some examples showcasing the interior of our buildings:

![int_ex1](/image/interior_showcase_1.png)
![int_ex2](/image/interior_showcase_2.png)
![int_ex3](/image/interior_showcase_3.png)

### Showcase Exterior

Lastly, to test the exterior structures in our buildings we can run:

```bash
python3 -m showcase_exterior
```
Likewise, this code produces random house confugurations in our build area. In order to visualize only the exterior, we generate only the garden room of our houses. Since, the exterior structure placements was successive instead of simultaneous (contrary to the interior structure generation) we encountered some issues were the placement rules were not appropriately taken into account. In order to validate the exterior structure placements we allowed for this code to either use similar sized gardens or sizes drawn randomly from uniform dstribution. The later case was useful, as we could easily test a variety of generated gardens and indentify any possible problems. Some generated examples can be seem in the ./image folder. 


Some examples showcasing the exterior of our buildings for same sized gardens:

![ext_ex1](/image/exterior_showcase_1.png)
![ext_ex2](/image/exterior_showcase_2.png)
![ext_ex3](/image/exterior_showcase_3.png)

Similarly, when drawing the sizes of the garden randomly from uniform distriutions we can get the following example images:

![ext_ex11](/image/exterior_showcase_rnd_size_1.png)
![ext_ex22](/image/exterior_showcase_rnd_size_2.png)
