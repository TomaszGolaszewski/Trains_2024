import pygame
import math
import random

from settings import *
from global_variables import *
# from classes_hex import *
from functions_math import *

class Tile:
    def __init__(self, id, coord_id, coord_world, dict_with_tracks={}, type="grass"):
        """Initialization of the tile."""
        self.id = id
        self.coord_id = coord_id
        self.coord_world = coord_world
        self.tile_type = type
        self.set_type(type)

        self.dict_with_tracks = dict_with_tracks

    def draw(self, win, offset_x: int, offset_y: int, scale):
        """Draw the Tile on the screen."""
        coord_screen = world2screen(self.coord_world, offset_x, offset_y, scale) 
        # draw background
        pygame.draw.circle(win, self.color, coord_screen, 50*scale)
        # draw tracks
        for track_angle in self.dict_with_tracks:
            pygame.draw.line(win, RED, coord_screen, move_point(coord_screen, 60*scale, math.radians(track_angle)), int(8*scale))


    def set_type(self, type, depth=0):
        """Set color of the tile depending on the type of terrain."""
        self.type = type
        self.depth = depth
        if type == "mars": self.color = [MARS_RED[0] - random.randint(0, 20), MARS_RED[1] + random.randint(0, 20), MARS_RED[2]]
        elif type == "snow": self.color = [SNOW_WHITE[0] - random.randint(0, 40), SNOW_WHITE[1] - random.randint(0, 10), SNOW_WHITE[2] - random.randint(0, 5)]
        elif type == "sand": self.color = [SAND[0] - random.randint(0, 15), SAND[1] - random.randint(0, 15), SAND[2] - random.randint(0, 15)]
        elif type == "grass": self.color = [GRASS[0], GRASS[1] - random.randint(0, 10), GRASS[2] - random.randint(0, 10)]
        # elif type == "forest": self.color = [GREEN[0], GREEN[1] - random.randint(0, 20), GREEN[2]]
        elif type == "forest": self.color = [GRASS[0], GRASS[1] - random.randint(0, 10) - 10, GRASS[2] - random.randint(0, 10)]
        elif type == "snow_forest": self.color = [SNOW_WHITE[0] - random.randint(0, 40) - 20, SNOW_WHITE[1] - random.randint(0, 10) - 10, SNOW_WHITE[2] - random.randint(0, 5)]
        elif type == "concrete": 
            rand = random.randint(0, 10)
            self.color = [GRAY[0] - rand, GRAY[1] - rand, GRAY[2] - rand]
        elif type == "submerged_concrete":
            rand = random.randint(0, 10)
            # self.color = [GRAY[0] - rand, GRAY[1] - rand, GRAY[2] - rand]
            self.color = [SHALLOW[0]- 4 * depth - rand, SHALLOW[1] - 8 * depth - rand, SHALLOW[2] - 8 * depth - rand] 
        elif type == "water": 
            depth -= 5
            self.color = [WATER[0], WATER[1] - 4 * depth, WATER[2] - 8 * depth]
        elif type == "shallow": 
            self.color = [SHALLOW[0]- 4 * depth, SHALLOW[1] - 8 * depth, SHALLOW[2] - 8 * depth]        
        else: self.color = RED

# ======================================================================

class Map:
    def __init__(self, tile_edge_length=60):
        """Initialization of the map."""

        self.tile_edge_length = tile_edge_length
        self.outer_tile_radius = tile_edge_length # outer radius = length of the edge
        self.inner_tile_radius = tile_edge_length * SQRT3 / 2 # inner radius

        # self.world = {}
        # 0, 60, 120, 180, 240, 300
        self.list_with_tiles = {
            1: Tile(1, (0, 0), self.id2world((0, 0)), {}, "water"),

            2: Tile(2, (1, 0), self.id2world((1, 0)), {0: 120, 120: 0}),
            3: Tile(3, (2, 0), self.id2world((2, 0)), {0: 180, 180: 0}, "snow"),
            4: Tile(4, (3, 0), self.id2world((3, 0)), {0: 180, 180: 0}),
            5: Tile(5, (4, 0), self.id2world((4, 0)), {0: 180, 180: 0}, "snow"),
            6: Tile(6, (5, 0), self.id2world((5, 0)), {0: 180, 180: 0, 0: 60, 60: 0}),
            7: Tile(7, (6, 0), self.id2world((6, 0)), {0: 180, 180: 0}),

            8: Tile(8, (0, 1), self.id2world((0, 1)), {120: 300, 300: 120}),
            9: Tile(9, (0, 2), self.id2world((0, 2)), {60: 300, 300: 60}, "snow"),
            10: Tile(10, (0, 3), self.id2world((0, 3)), {120: 240, 240: 120}),
            11: Tile(11, (0, 4), self.id2world((0, 4)), {60: 300, 300: 60}),
            12: Tile(12, (0, 5), self.id2world((0, 5)), {120: 240, 240: 120}),

            13: Tile(13, (4, 3), self.id2world((4, 3))),

            14: Tile(14, (-1, 0), self.id2world((-1, 0)), {}, "water"),
            15: Tile(15, (-2, 0), self.id2world((-2, 0)), {}, "water"),
        }
        self.lowest_free_id = 16

    def draw(self, win, offset_x: int, offset_y: int, scale):
        """Draw the Map on the screen."""
        for tile_id in self.list_with_tiles:
            self.list_with_tiles[tile_id].draw(win, offset_x, offset_y, scale)

    def add_tile(self, coord_world, terrain):
        coord_id = self.world2id(coord_world)
        self.list_with_tiles[self.lowest_free_id] = Tile(self.lowest_free_id, coord_id, self.id2world(coord_id), {}, terrain)
        self.lowest_free_id += 1
        # TODO:

    def id2world(self, coord_id: tuple[int, int]) -> tuple[float, float]:
        """
        Calculate coordinates from tile's id to world coordinate system.
        Return coordinates in the world coordinate system.
        """
        x_id, y_id = coord_id

        if y_id % 2:
            x_world = (2 * x_id + 1) * self.inner_tile_radius
        else:
            x_world = 2 * x_id * self.inner_tile_radius

        y_world = 3 / 2 * self.outer_tile_radius * y_id

        return (x_world, y_world)

    def world2id(self, coord_world: tuple[float, float]) -> tuple[int, int]:
        """
        Calculate coordinates from world coordinate system to tile's id.
        Return tile's id coordinates.
        """
        x_world, y_world = coord_world
        
        y_id = int(2 / 3 * y_world / self.outer_tile_radius + 0.5)

        if y_id % 2:
            x_id = int(x_world / self.inner_tile_radius / 2)
        else:
            x_id = int(x_world / self.inner_tile_radius / 2 + 0.5)

        return (x_id, y_id)