import pygame
import math
import random

from settings import *
from global_variables import *
from functions_math import *
from classes_trains import *

class Tile:
    # def __init__(self, id, coord_id, coord_world, list_with_tracks=None, type="grass"):
    def __init__(self, map, id: int, coord_id: tuple[int, int], list_with_tracks: list = None, type: str = "grass"):
        """Initialization of the tile."""
        self.id = id
        self.coord_id = coord_id
        self.coord_world = map.id2world(coord_id)
        self.tile_type = type
        self.set_type(type)

        if list_with_tracks is None: self.list_with_tracks = []
        else: self.list_with_tracks = list_with_tracks

        # labels
        self.font_obj = pygame.font.SysFont("arial", 20)

    def draw(self, win, offset_x: int, offset_y: int, scale: float):
        """Draw the Tile on the screen."""
        coord_screen = world2screen(self.coord_world, offset_x, offset_y, scale) 
        # draw background
        pygame.draw.circle(win, self.color, coord_screen, 50*scale)
        # draw label
        if scale >= 0.5:
            text_obj = self.font_obj.render(f"{self.id}", True, self.color, BLACK) # {self.coord_id} {self.list_with_tracks}
            win.blit(text_obj, coord_screen)

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

class World_map:
    def __init__(self, tile_edge_length=60):
        """Initialization of the map."""

        self.tile_edge_length = tile_edge_length
        self.outer_tile_radius = tile_edge_length # outer radius = length of the edge
        self.inner_tile_radius = tile_edge_length * SQRT3 / 2 # inner radius

        self.dict_with_tiles = {}
        self.dict_with_trains = {}

    def draw(self, win, offset_x: int, offset_y: int, scale):
        """Draw the World Map on the screen."""
        # draw tiles
        for tile_id in self.dict_with_tiles:
            tile = self.dict_with_tiles[tile_id]
            tile.draw(win, offset_x, offset_y, scale)
            # draw tracks
            coord_screen = world2screen(tile.coord_world, offset_x, offset_y, scale)
            for neighbor_tile_id in tile.list_with_tracks:
                neighbor_coord_screen = world2screen(self.dict_with_tiles[neighbor_tile_id].coord_world, offset_x, offset_y, scale)
                pygame.draw.line(win, RED, coord_screen, neighbor_coord_screen, int(12*scale))
        # draw trains
        for train_id in self.dict_with_trains:
            self.dict_with_trains[train_id].draw(win, self, offset_x, offset_y, scale)

    def add_tile(self, coord_id: tuple[int, int], terrain: str) -> int:
        """Add new tile. If the tile exists, change its type.
        Return ID of the created/updated tile."""
        tile_id = self.get_tile_by_coord_id(coord_id)
        if not tile_id:
            self.dict_with_tiles[self.lowest_free_id] = Tile(self.lowest_free_id, coord_id, self.id2world(coord_id), [], terrain)
            self.lowest_free_id += 1
            return self.lowest_free_id - 1
        elif self.dict_with_tiles[tile_id].type != terrain:
            self.dict_with_tiles[tile_id].set_type(terrain)
            return tile_id

    def remove_tile(self, tile_id: int):
        """Remove tile with all connected tracks."""
        # remove tracks
        for neighbor_tile_id in self.dict_with_tiles[tile_id].list_with_tracks:
            if tile_id in self.dict_with_tiles[neighbor_tile_id].list_with_tracks:
                self.dict_with_tiles[neighbor_tile_id].list_with_tracks.remove(tile_id)
        # remove tile
        del self.dict_with_tiles[tile_id]

    def add_track(self, first_tile_id: int, second_tile_id: int):
        """Add new track (connection between tiles) by adding ids of connected 
        tiles to lists of tracks of each track."""
        if second_tile_id not in self.dict_with_tiles[first_tile_id].list_with_tracks:
            self.dict_with_tiles[first_tile_id].list_with_tracks.append(second_tile_id)
        if first_tile_id not in self.dict_with_tiles[second_tile_id].list_with_tracks:
            self.dict_with_tiles[second_tile_id].list_with_tracks.append(first_tile_id)

    def remove_track(self, first_tile_id: int, second_tile_id: int):
        """Remove track (connection between tiles) by removing ids of connected 
        tiles from lists of tracks of each track."""
        if second_tile_id in self.dict_with_tiles[first_tile_id].list_with_tracks:
            self.dict_with_tiles[first_tile_id].list_with_tracks.remove(second_tile_id)
        if first_tile_id in self.dict_with_tiles[second_tile_id].list_with_tracks:
            self.dict_with_tiles[second_tile_id].list_with_tracks.remove(first_tile_id)

    def get_tile_by_coord_id(self, coord_id: tuple[int, int]) -> int:
        """Return ID of tile indicated by ordinal coordinates."""
        for tile_id in self.dict_with_tiles:
            if self.dict_with_tiles[tile_id].coord_id == coord_id:
                return self.dict_with_tiles[tile_id].id
        return False
    
    def get_track_by_coord_world(self, coord_world: tuple[float, float]) -> tuple[int, int]:
        """Return pair of IDs of tiles indicated by global (world) coordinates."""
        # find the first tile
        first_tile_coord_id = self.world2id(coord_world)
        first_tile_id = self.get_tile_by_coord_id(first_tile_coord_id)
        if not first_tile_id: return False, False
        # find the second tile
        dist_to_closest = 9999
        id_of_closest = 0
        for tile_id in self.dict_with_tiles:
            dist = dist_two_points(coord_world, self.dict_with_tiles[tile_id].coord_world)
            if dist < dist_to_closest and tile_id != first_tile_id:
                dist_to_closest = dist
                id_of_closest = tile_id
        if id_of_closest:
            return first_tile_id, id_of_closest
        # no tile found
        return False, False

    def id2world(self, coord_id: tuple[int, int]) -> tuple[float, float]:
        """Calculate coordinates from tile's id to world coordinate system.
        Return coordinates in the world coordinate system."""
        x_id, y_id = coord_id
        if y_id % 2:
            x_world = (2 * x_id + 1) * self.inner_tile_radius
        else:
            x_world = 2 * x_id * self.inner_tile_radius
        y_world = 3 / 2 * self.outer_tile_radius * y_id
        return (x_world, y_world)

    def world2id(self, coord_world: tuple[float, float]) -> tuple[int, int]:
        """Calculate coordinates from world coordinate system to tile's id.
        Return tile's id coordinates."""
        x_world, y_world = coord_world
        y_id = math.floor(2 / 3 * y_world / self.outer_tile_radius + 0.5)
        if y_id % 2:
            x_id = math.floor(x_world / self.inner_tile_radius / 2)
        else:
            x_id = math.floor(x_world / self.inner_tile_radius / 2 + 0.5)
        return (x_id, y_id)
    
    def extrapolate_tile_position_in_line(self, coord_1: tuple[int, int], 
                                coord_2: tuple[int, int]) -> tuple[int, int]:
        """Extrapolate the position of the tile in straight line 
        based on the position of the two previous ones.
        """
        x1, y1 = coord_1
        x2, y2 = coord_2
        dx = x2 - x1
        dy = y2 - y1

        if y1 == y2: 
            return (x2+dx, y1)
        elif y1 % 2:
            return (x2+dx-1, y2+dy)
        else:
            return (x2+dx+1, y2+dy)

    def extrapolate_tile_position_with_coord(self, coord_id_1: tuple[int, int], 
                        coord_id_2: tuple[int, int], turn: str = "center") -> tuple[int, int]:
        """Extrapolate the position of the tile based on the position of the two previous ones.
        Possible turns: left, right, center."""
        coord_world_1 = self.id2world(coord_id_1)
        coord_world_2 = self.id2world(coord_id_2)
        angle = angle_to_target(coord_world_1, coord_world_2)
        delta_angle = 0
        if turn == "right": delta_angle = math.pi/3
        if turn == "left": delta_angle = -math.pi/3
        coord_world_3 = move_point(coord_world_2, 2 * self.inner_tile_radius, angle + delta_angle)
        return self.world2id(coord_world_3)
    
    def extrapolate_tile_position_with_id(self, id_1: int, id_2: int, turn: str = "center") -> id:
        """Extrapolate the ID of the tile based on the IDs of the two previous ones.
        Possible turns: left, right, center."""
        coord_world_2 = self.dict_with_tiles[id_2].coord_world
        angle = angle_to_target(self.dict_with_tiles[id_1].coord_world, coord_world_2)
        delta_angle = 0
        if turn == "right": delta_angle = math.pi/3
        if turn == "left": delta_angle = -math.pi/3
        coord_world_3 = move_point(coord_world_2, 2 * self.inner_tile_radius, angle + delta_angle)
        return self.get_tile_by_coord_id(self.world2id(coord_world_3))
    
    def find_route(self, target_tile_id: int, last_tile_id: int, current_tile_id: int, \
                        search_history: list[tuple[int, str]] = [], countdown: int = 100) -> list[int]:
        """Recursive function that searches for a train route. 
        The search is interrupted if the function finds a target, or is called too many times, 
        or detects that the train is running in a loop."""
        # check if the recursion is not too deep
        if not countdown: return []
        # check angles and switches first
        for track_turn in ["right", "center", "left"]:
            next_tile_id = self.extrapolate_tile_position_with_id(last_tile_id, current_tile_id, turn=track_turn)
            if next_tile_id in self.dict_with_tiles[current_tile_id].list_with_tracks:
                # check if next tile is the target
                if next_tile_id == target_tile_id: return [next_tile_id]
                # check if the train is running in loop
                if track_turn != "center" and (current_tile_id, track_turn) in search_history: return []
                # run the recursion
                path = self.find_route(target_tile_id, current_tile_id, next_tile_id, \
                                        search_history + [(current_tile_id, track_turn)], countdown-1)
                if path: return [next_tile_id] + path
        return []

    def find_next_track(self, last_tile_id: int, current_tile_id: int) -> int:
        """Find and return the next tile on the route."""
        for track_turn in ["right", "center", "left"]:
            next_tile_id = self.extrapolate_tile_position_with_id(last_tile_id, current_tile_id, turn=track_turn)
            if next_tile_id in self.dict_with_tiles[current_tile_id].list_with_tracks:
                return next_tile_id
        return 0

    def calculate_trains_path(self):
        """Calls methods calculating the route for all trains."""
        dict_with_reservations = {}
        for train_id in self.dict_with_trains:
            self.dict_with_trains[train_id].find_movement_whole_path(self)
            self.dict_with_trains[train_id].find_movement_free_path(self, self.dict_with_trains, dict_with_reservations)
            