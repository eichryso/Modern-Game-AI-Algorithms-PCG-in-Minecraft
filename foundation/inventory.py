import logging
from random import randint
import numpy as np

from gdpc import Block, Editor
from gdpc import geometry as geo
from gdpc import minecraft_tools as mt
from gdpc import editor_tools as et


logging.basicConfig(format="%(name)s - %(levelname)s - %(message)s")

ED = Editor(buffering=True)

def material(use = None):
    if use == "bookshelf":
        resource_location_names = [
            "minecraft:bookshelf"
        ]
    elif use == "bush":
        resource_location_names = [
            "minecraft:moss_block"
        ]
    elif use == "light":
        resource_location_names = [
            "minecraft:lantern",
            "minecraft:soul_lantern"
        ]
    elif use == "torch":
        resource_location_names = [
            "minecraft:torch",
            "minecraft:soul_torch",
            "minecraft:redstone_torch"
        ]
    elif use == "garden_floor":
        resource_location_names = [
            "minecraft:grass_block",
            "minecraft:moss_block",
            "minecraft:dirt",
            "minecraft:podzol",
            "minecraft:coarse_dirt"
            ]
    elif use =="crop":
        resource_location_names = [
            "minecraft:wheat",
            "minecraft:carrots",
            "minecraft:potatoes",
            "minecraft:beetroots",
            "minecraft:bamboo"
        ]
    elif use == "crop_floor":
        resource_location_names = [
            "minecraft:farmland",
            "minecraft:farmland",
            "minecraft:farmland",
            "minecraft:farmland",
            "minecraft:grass_block"
        ]
    elif use == "bed":
        resource_location_names = [
            "minecraft:red_bed",
            "minecraft:gray_bed",
            "minecraft:light_blue_bed",
            "minecraft:light_gray_bed",
            "minecraft:lime_bed",
            "minecraft:orange_bed"
        ]
    elif use == "wood":
        resource_location_names = [
            "minecraft:oak_log",
            "minecraft:spruce_log",
            "minecraft:birch_log",
            "minecraft:jungle_log",
            "minecraft:acacia_log",
            "minecraft:dark_oak_log",
            "minecraft:mangrove_log",
            "minecraft:cherry_log"
        ]
    elif use == "carpet":
        resource_location_names = [
            "minecraft:lime_carpet",
            "minecraft:pink_carpet",
            "minecraft:gray_carpet",
            "minecraft:cyan_carpet",
            "minecraft:white_carpet",
            "minecraft:brown_carpet",
            "minecraft:black_carpet",
            "minecraft:moss_carpet"
        ]
    elif use == "fence":
        resource_location_names = [
            "minecraft:oak_fence",
            "minecraft:spruce_fence",
            "minecraft:birch_fence",
            "minecraft:jungle_fence",
            "minecraft:acacia_fence",
            "minecraft:dark_oak_fence",
            "minecraft:mangrove_fence",
            "minecraft:cherry_fence",
            "minecraft:crimson_fence",
            "minecraft:warped_fence"
        ]
    elif use == "stairs":
        resource_location_names = [
            "minecraft:oak_stairs",
            "minecraft:spruce_stairs",
            "minecraft:birch_stairs",
            "minecraft:jungle_stairs",
            "minecraft:acacia_stairs",
            "minecraft:dark_oak_stairs",
            "minecraft:mangrove_stairs",
            "minecraft:cherry_stairs",
            "minecraft:bamboo_stairs",
            "minecraft:crimson_stairs",
            "minecraft:warped_stairs"
        ]
    elif use == "door_fence":
        resource_location_names = [
            "minecraft:oak_fence_gate",
            "minecraft:spruce_fence_gate",
            "minecraft:birch_fence_gate",
            "minecraft:jungle_fence_gate",
            "minecraft:acacia_fence_gate",
            "minecraft:dark_oak_fence_gate",
            "minecraft:mangrove_fence_gate",
            "minecraft:cherry_fence_gate",
            "minecraft:crimson_fence_gate",
            "minecraft:warped_fence_gate"
        ]
    elif use == "flower":
        resource_location_names = [
            "minecraft:poppy",
            "minecraft:dandelion",
            "minecraft:azure_bluet",
            "minecraft:cornflower",
            "minecraft:allium",
            "minecraft:oxeye_daisy",
            "minecraft:red_tulip",
            "minecraft:white_tulip",
            "minecraft:orange_tulip",
            "minecraft:pink_tulip"
        ]
    elif use == "door":        
        resource_location_names = [
            "minecraft:oak_door",
            "minecraft:spruce_door",
            "minecraft:birch_door",
            "minecraft:jungle_door",
            "minecraft:acacia_door",
            "minecraft:dark_oak_door",
            "minecraft:mangrove_door",
            "minecraft:cherry_door",
            "minecraft:bamboo_door",
            "minecraft:crimson_door",
            "minecraft:warped_door"
        ]
    elif use == "window":
        resource_location_names = [
            "minecraft:glass",
            "minecraft:glass_pane",
            "minecraft:white_stained_glass",
            "minecraft:white_stained_glass_pane",
            "minecraft:light_gray_stained_glass",
            "minecraft:light_gray_stained_glass_pane",
            "minecraft:gray_stained_glass",
            "minecraft:gray_stained_glass_pane",
            "minecraft:black_stained_glass",
            "minecraft:black_stained_glass_pane",
            "minecraft:brown_stained_glass",
            "minecraft:brown_stained_glass_pane",
            "minecraft:red_stained_glass",
            "minecraft:red_stained_glass_pane",
            "minecraft:orange_stained_glass",
            "minecraft:orange_stained_glass_pane",
            "minecraft:yellow_stained_glass",
            "minecraft:yellow_stained_glass_pane",
            "minecraft:lime_stained_glass",
            "minecraft:lime_stained_glass_pane",
            "minecraft:green_stained_glass",
            "minecraft:green_stained_glass_pane",
            "minecraft:cyan_stained_glass",
            "minecraft:cyan_stained_glass_pane",
            "minecraft:light_blue_stained_glass",
            "minecraft:light_blue_stained_glass_pane",
            "minecraft:blue_stained_glass",
            "minecraft:blue_stained_glass_pane",
            "minecraft:purple_stained_glass",
            "minecraft:purple_stained_glass_pane",
            "minecraft:magenta_stained_glass",
            "minecraft:magenta_stained_glass_pane",
            "minecraft:pink_stained_glass",
            "minecraft:pink_stained_glass_pane"
        ]
    elif use == "roof":
        resource_location_names = [
            "minecraft:oak_planks",
            "minecraft:spruce_planks",
            "minecraft:birch_planks",
            "minecraft:jungle_planks",
            "minecraft:acacia_planks",
            "minecraft:dark_oak_planks",
            "minecraft:mangrove_planks",
            "minecraft:cherry_planks",
            "minecraft:bamboo_planks",
            "minecraft:crimson_planks",
            "minecraft:warped_planks",
            "minecraft:oak_wood",
            "minecraft:spruce_wood",
            "minecraft:birch_wood",
            "minecraft:jungle_wood",
            "minecraft:acacia_wood",
            "minecraft:dark_oak_wood",
            "minecraft:mangrove_wood",
            "minecraft:cherry_wood",
            "minecraft:bamboo_block",
            "minecraft:cobblestone",
            "minecraft:stone_bricks",
            "minecraft:deepslate_tiles",
            "minecraft:deepslate_bricks",
            "minecraft:polished_blackstone_bricks",
            "minecraft:bricks",
            "minecraft:mud_bricks",
            "minecraft:nether_bricks",
            "minecraft:red_nether_bricks",
            "minecraft:quartz_block",
            "minecraft:smooth_quartz",
            "minecraft:copper_block",
            "minecraft:exposed_copper",
            "minecraft:weathered_copper",
            "minecraft:oxidized_copper"
        ]
    elif use == "wall" or use == "foundation":
        resource_location_names = [
            "minecraft:stone",
            "minecraft:cobblestone",
            "minecraft:mossy_cobblestone",
            "minecraft:stone_bricks",
            "minecraft:mossy_stone_bricks",
            "minecraft:cracked_stone_bricks",
            "minecraft:chiseled_stone_bricks",
            "minecraft:bricks",
            "minecraft:mud_bricks",
            "minecraft:nether_bricks",
            "minecraft:red_nether_bricks",
            "minecraft:end_stone_bricks",
            "minecraft:smooth_quartz",
            "minecraft:quartz_block",
            "minecraft:chiseled_quartz_block",
            "minecraft:sandstone",
            "minecraft:smooth_sandstone",
            "minecraft:cut_sandstone",
            "minecraft:red_sandstone",
            "minecraft:smooth_red_sandstone",
            "minecraft:granite",
            "minecraft:polished_granite",
            "minecraft:diorite",
            "minecraft:polished_diorite",
            "minecraft:andesite",
            "minecraft:polished_andesite",
            "minecraft:cobbled_deepslate",
            "minecraft:polished_deepslate",
            "minecraft:deepslate_bricks",
            "minecraft:deepslate_tiles",
            "minecraft:cracked_deepslate_bricks",
            "minecraft:cracked_deepslate_tiles",
            "minecraft:blackstone",
            "minecraft:polished_blackstone",
            "minecraft:polished_blackstone_bricks",
            "minecraft:chiseled_polished_blackstone",
            "minecraft:white_concrete",
            "minecraft:gray_concrete",
            "minecraft:light_gray_concrete",
            "minecraft:black_concrete",
            "minecraft:brown_concrete",
            "minecraft:terracotta",
            "minecraft:white_terracotta",
            "minecraft:gray_terracotta",
            "minecraft:black_terracotta",
            "minecraft:brown_terracotta",
            "minecraft:oak_planks",
            "minecraft:spruce_planks",
            "minecraft:birch_planks",
            "minecraft:jungle_planks",
            "minecraft:acacia_planks",
            "minecraft:dark_oak_planks",
            "minecraft:mangrove_planks",
            "minecraft:cherry_planks",
            "minecraft:bamboo_planks",
            "minecraft:crimson_planks",
            "minecraft:warped_planks"
        ]
    material = np.random.choice(resource_location_names)
    return material

    
