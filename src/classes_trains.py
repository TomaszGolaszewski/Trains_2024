import pygame
import math
import random

# from settings import *
from global_variables import *
from functions_math import *

class Train:
    def __init__(self, map, id: int, tile_id: int, last_tile_id: int):
        """Initialization of the train."""

        # position on the map
        self.id = id
        self.tile_id = tile_id
        self.last_tile_id = last_tile_id
        self.coord_world = map.dict_with_tiles[tile_id].coord_world
        last_tile_coord_world = map.dict_with_tiles[last_tile_id].coord_world
        self.angle = angle_to_target(last_tile_coord_world, self.coord_world)

        # movement parameters
        self.state = "stop" # "no_path"
        self.v_max = 3
        self.v_target = 0
        self.v_current = 0
        self.acceleration = 0.02
        self.turn_speed = 0.01
        self.movement_target = [] # main target of the unit movement
        self.movement_path = [] # path to the closest target

        # labels
        list_with_colors = [BLUE, YELLOW, ORANGE, GREEN, HOTPINK]
        self.color = list_with_colors[random.randint(0, len(list_with_colors) - 1)]
        self.font_obj = pygame.font.SysFont("arial", 20)
        self.button_array_origin = (5, 30)
        self.button_height = 40
        self.button_width = 40
        self.button_icon_radius = 15

    def draw(self, win, map, offset_x: int, offset_y: int, scale):
        """Draw the train on the screen."""
        coord_screen = world2screen(self.coord_world, offset_x, offset_y, scale) 
        # draw train as symbol
        pygame.draw.circle(win, self.color, coord_screen, 40*scale)
        pygame.draw.line(win, BLACK, coord_screen, move_point(coord_screen, 30*scale, self.angle), int(8*scale))
        # draw label
        if scale >= 0.25:
            text_obj = self.font_obj.render(f"{self.state} {self.v_current:.2f} > {self.v_target} ", True, self.color, BLACK) # {self.movement_path} {self.movement_target} 
            win.blit(text_obj, (coord_screen[0] + 15, coord_screen[1] + 10))
        # draw tracks on path
        for tile_id in self.movement_path:
            pygame.draw.circle(win, self.color, world2screen(map.dict_with_tiles[tile_id].coord_world, offset_x, offset_y, scale) , 10*scale)
        # draw targets
        for tile_id in self.movement_target:
            pygame.draw.circle(win, self.color, world2screen(map.dict_with_tiles[tile_id].coord_world, offset_x, offset_y, scale) , 30*scale)

    def draw_button(self, win, number_on_screen: int):
        """Draw train button."""
        center = (self.button_array_origin[0] + self.button_width // 2, \
                    self.button_array_origin[1] + self.button_height // 2 + self.button_height * number_on_screen)
        pygame.draw.circle(win, self.color, center, self.button_icon_radius)
        pygame.draw.line(win, BLACK, center, move_point(center, self.button_icon_radius, self.angle), 4)

    def draw_button_selection(self, win, number_on_screen: int):
        """Draw train button selection."""
        center = (self.button_array_origin[0] + self.button_width // 2, \
                    self.button_array_origin[1] + self.button_height // 2 + self.button_height * number_on_screen)
        pygame.draw.circle(win, LIME, center, self.button_height, 4)

    def is_button_pressed(self, coord_on_screen: tuple[float, float], number_on_screen: int) -> bool:
        """Return True if train button is pressed."""
        x, y = coord_on_screen
        if self.button_array_origin[0] < x and x < self.button_array_origin[0] + self.button_width and \
                self.button_array_origin[1] + self.button_height * number_on_screen < y and \
                y < self.button_array_origin[1] + self.button_height * (number_on_screen + 1):
            return True
        return False

    def run(self, map, dict_with_trains):
        """Life-cycle of the train."""

        # check position
        coord_id = map.world2id(self.coord_world)
        current_tile_id = map.get_tile_by_coord_id(coord_id)
        if current_tile_id and current_tile_id != self.tile_id:
            self.last_tile_id = self.tile_id
            self.tile_id = current_tile_id

        # check collisions
        self.check_collisions(dict_with_trains)

        # check current movement target
        if len(self.movement_target):
            if map.dict_with_tiles[self.movement_target[0]].coord_id == coord_id:
                self.movement_target.pop(0) # remove the achieved target

        # find path
        if len(self.movement_target):
            self.movement_path = map.find_route(self.movement_target[0], self.last_tile_id, self.tile_id)
        else:
            self.movement_path = []

        # check current movement path
        if len(self.movement_path):
            if map.dict_with_tiles[self.movement_path[0]].coord_id == coord_id:
                self.movement_path.pop(0) # remove the achieved tile

        # set parameters related to train movement
        self.set_velocity()
        self.set_turn_velocity()
        self.accelerate()
        self.set_state()

        # move the train
        if len(self.movement_path):  
            self.angle = self.get_new_angle(map.dict_with_tiles[self.movement_path[0]].coord_world)
        self.coord_world = move_point(self.coord_world, self.v_current, self.angle)

    def check_collisions(self, dict_with_trains):
        """Check collisions with other trains."""
        for train_id in dict_with_trains:
            if train_id != self.id and dict_with_trains[train_id].tile_id == self.tile_id:
                self.state = "broken"
                self.v_target = 0
                self.v_current = 0
                self.movement_path = []
                self.movement_target = []
                self.color = RED

    def set_velocity(self):
        """Set target velocity based on distance to target."""
        dist = len(self.movement_path)
        if not dist: self.v_target = 0
        elif dist < self.v_max: self.v_target = dist
        else: self.v_target = self.v_max

    def set_turn_velocity(self):
        """Set turn velocity based on current linear speed."""
        self.turn_speed = self.v_current / 80

    def set_state(self):
        """Set train status."""
        if self.state != "broken":
            if self.state == "stop" and self.v_current != 0: self.state = "move"
            elif self.state == "move" and self.v_target == 0 and self.v_current == 0: self.state = "stop"

    def accelerate(self):
        """Accelerate the train - calculate the current speed."""
        if self.state != "broken":
            if self.v_target > self.v_current:
                self.v_current += self.acceleration
                if self.v_target < self.v_current: self.v_current = self.v_target
            if self.v_target < self.v_current:
                self.v_current -= self.acceleration
                if self.v_target > self.v_current: self.v_current = self.v_target

    def get_new_angle(self, coord_target: tuple[float, float]) -> float:
        """Return new angle closer to the movement target."""
        target_angle = angle_to_target(self.coord_world, coord_target)
        return turn_to_target_angle(self.angle, target_angle, self.turn_speed)
