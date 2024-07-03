import pygame
import math
import random

# from settings import *
from global_variables import *
from functions_math import *

class Train:
    def __init__(self, id, coord_world, angle, color=RED):
        """Initialization of the train."""
        self.id = id
        self.coord_world = coord_world
        self.angle = angle # radians
        self.color = color

        self.v_current = 0
        self.v_max = 1
        self.acceleration = 0.1
        self.turn_speed = 0.01
        self.movement_path = []

    def draw(self, win, map, offset_x: int, offset_y: int, scale):
        """Draw the train on the screen."""
        coord_screen = world2screen(self.coord_world, offset_x, offset_y, scale) 
        # draw train as symbol
        pygame.draw.circle(win, self.color, coord_screen, 20*scale)
        pygame.draw.line(win, BLACK, coord_screen, move_point(coord_screen, 20*scale, self.angle), int(4*scale))
        # draw tracks
        for tile_id in self.movement_path:
            pygame.draw.circle(win, self.color, world2screen(map.list_with_tiles[tile_id].coord_world, offset_x, offset_y, scale) , 10*scale)

    def run(self, map):
        """Life-cycle of the train"""

        # check current movement path
        if len(self.movement_path):
            coord_id = map.world2id(self.coord_world)
            if map.list_with_tiles[self.movement_path[0]].coord_id == coord_id:
                self.movement_path.pop(0) # remove the achieved tile

        # move the train
        if len(self.movement_path):
            self.accelerate()
            self.angle = self.get_new_angle(map.list_with_tiles[self.movement_path[0]].coord_world)
        else: # if this was the last segment
            self.decelerate()
        self.coord_world = move_point(self.coord_world, self.v_current, self.angle)

    def accelerate(self):
        """Accelerate the train - calculate the current speed."""   
        self.v_current += self.acceleration
        if self.v_current > self.v_max: self.v_current = self.v_max

    def decelerate(self):
        """Decelerate the vehicle - calculate the current speed.""" 
        self.v_current -= self.acceleration
        if self.v_current < 0: 
            self.v_current = 0

    def get_new_angle(self, coord_target):
        """Return new angle closer to the movement target."""
        target_angle = angle_to_target(self.coord_world, coord_target)
        return turn_to_target_angle(self.angle, target_angle, self.turn_speed)
