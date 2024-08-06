import pygame
import requests

from settings import *
from classes_scenes_features import *
from classes_map import *


class SceneBase:
    def __init__(self):
        """Initialization of the scene."""
        self.next = self
    
    def process_input(self, events, keys_pressed):
        """
        Receive all the events that happened since the last frame.
        Handle all received events.
        """
        print("not overwritten process_input")

    def update(self):
        """Game logic for the scene."""
        print("not overwritten update")

    def render(self, win):
        """Draw scene on the screen."""
        print("not overwritten render")

    def switch_scene(self, next_scene):
        """Change scene."""
        self.next = next_scene
    
    def terminate(self):
        """Close the game by changing scene to None."""
        self.switch_scene(None)


# ======================================================================


class TitleScene(SceneBase):
    def __init__(self):
        """Initialization of the scene."""
        SceneBase.__init__(self)
        self.title = FixText((WIN_WIDTH/2, WIN_HEIGHT/2 - 30), "TRAINS 2024", 70)
        self.subtitle = FixText((WIN_WIDTH/2, WIN_HEIGHT/2 + 20), "Client Python", 40)
        # self.start_button = AdvancedButton((WIN_WIDTH/2, WIN_HEIGHT/2 + 100), "[Prepare Game]", 30, color=GRAY)
        self.quick_start_button = AdvancedButton((WIN_WIDTH/2, WIN_HEIGHT/2 + 150), "[Connect]", 30, color=GRAY)
        self.exit_button = AdvancedButton((WIN_WIDTH/2, WIN_HEIGHT/2 + 200), "[Exit]", 30, color=GRAY)
        self.seconds_since_start = 0
        self.current_frame = 0
        self.buttons_delay = 0 #1
    
    def process_input(self, events, keys_pressed):
        """
        Receive all the events that happened since the last frame.
        Handle all received events.
        """

        for event in events:
            # keys that can be pressed only ones
            if event.type == pygame.KEYDOWN:
        #         # move to the next scene
        #         if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
        #             self.switch_scene(ChooseMapScene())
                # quick start
                if event.key == pygame.K_q:
                    self.switch_scene(LoadingScene())

            # mouse button down
            if event.type == pygame.MOUSEBUTTONDOWN \
                        and self.seconds_since_start > self.buttons_delay \
                        and event.button in [1,2,3]: # 1 - left; 2 - middle; 3 - right click
                mouse_coord = pygame.mouse.get_pos()
                # move to the next scene
                # if self.start_button.is_inside(mouse_coord):
                #     self.switch_scene(ChooseMapScene())
                # quick start
                if self.quick_start_button.is_inside(mouse_coord):
                    self.switch_scene(LoadingScene())
                # exit
                if self.exit_button.is_inside(mouse_coord):
                    self.terminate()
                  
    def update(self):
        """Game logic for the scene."""

        # check hovering of the mouse
        mouse_coord = pygame.mouse.get_pos()
        # self.start_button.check_hovering(mouse_coord)
        self.quick_start_button.check_hovering(mouse_coord)
        self.exit_button.check_hovering(mouse_coord)

        self.current_frame += 1
        if self.current_frame == FRAMERATE:
            self.current_frame = 0
            self.seconds_since_start += 1

    def render(self, win):
        """Draw scene on the screen."""

        # clear screen
        win.fill(BLACK)

        # print titles and buttons
        self.title.draw(win)
        self.subtitle.draw(win)
        if self.seconds_since_start > self.buttons_delay:
            # self.start_button.draw(win)
            self.quick_start_button.draw(win)
            self.exit_button.draw(win)


# ======================================================================


class LoadingScene(SceneBase):
    def __init__(self):
        """Initialization of the scene."""
        SceneBase.__init__(self)
        self.loading_text = FixText((WIN_WIDTH/2, WIN_HEIGHT/2), "Loading ...", 30)
        self.ticks = 0
    
    def process_input(self, events, keys_pressed):
        """
        Receive all the events that happened since the last frame.
        Handle all received events.
        """
        pass

    def update(self):
        """Game logic for the scene."""
        self.ticks += 1
        # automatically jump to the GameScene after the first cycle
        if self.ticks > 1:
            self.switch_scene(GameScene())
    
    def render(self, win):
        """Draw scene on the screen."""
        # clear screen
        win.fill(BLACK)
        # print loading text
        self.loading_text.draw(win)


# ======================================================================


class GameScene(SceneBase):
    def __init__(self):
        """Initialization of the scene."""
        SceneBase.__init__(self)

        # display variables
        self.scale = 0.5
        self.offset_horizontal, self.offset_vertical = 500, 500
        # self.show_extra_data = False
        # self.show_movement_target = False
        # self.pause = False
        self.current_frame = 0

        # create mode buttons
        mode_list = ["none", "terrain", "tracks", "trains", "targets"]
        self.list_with_mode_buttons = []
        for i, mode in enumerate(mode_list):
            self.list_with_mode_buttons.append(AdvancedButton((WIN_WIDTH - 770 + 170*i, 40), "["+mode.capitalize()+"]", 30, color=GRAY, option=mode, width=150))
        # set first map as active as default
        self.list_with_mode_buttons[0].active = True
        self.current_mode = mode_list[0]

        # create terrain buttons
        terrain_list = ["snow", "grass", "sand", "water", "concrete", "mars"]
        self.list_with_terrain_buttons = []
        for i, terrain in enumerate(terrain_list):
            self.list_with_terrain_buttons.append(AdvancedButton((WIN_WIDTH - 940 + 170*i, 100), "["+terrain.capitalize()+"]", 30, color=GRAY, option=terrain, width=150))
        # set first terrain as active as default
        self.list_with_terrain_buttons[0].active = True
        self.current_terrain = terrain_list[0]

        # mouse related variables
        self.left_mouse_button_down = False
        self.right_mouse_button_down = False
        self.last_used_tile = 0

        # initialize the map
        self.map = World_map()
        self.current_selected_train_id = 0
        self.lowest_free_train_id = 1

        # TODO: check and remove
        self.list_with_windows = []
    

    def process_input(self, events, keys_pressed):
        """
        Receive all the events that happened since the last frame.
        Handle all received events.
        """

        # calculate values ​​for mouse and tile position
        mouse_pos = pygame.mouse.get_pos()
        coord_world = screen2world(mouse_pos, self.offset_horizontal, self.offset_vertical, self.scale)
        coord_id = self.map.world2id(coord_world)
        current_tile_id = self.map.get_tile_by_coord_id(coord_id)

        for event in events:

            # mouse button down
            if event.type == pygame.MOUSEBUTTONDOWN:
                # # 1 - left click
                # if event.button == 1:
                #     button_was_pressed = False
                #     # choose mode
                #     if any([mode_button.is_inside(mouse_pos) for mode_button in self.list_with_mode_buttons]):
                #         button_was_pressed = True
                #         for mode_button in self.list_with_mode_buttons:
                #             if mode_button.check_pressing(mouse_pos):
                #                 self.current_mode = mode_button.option
                #     # choose terrain
                #     if self.current_mode == "terrain" and \
                #             any([terrain_button.is_inside(mouse_pos) for terrain_button in self.list_with_terrain_buttons]):
                #         button_was_pressed += True
                #         for terrain_button in self.list_with_terrain_buttons:
                #             if terrain_button.check_pressing(mouse_pos):
                #                 self.current_terrain = terrain_button.option
                #     # choose train
                #     for i, train_id in enumerate(self.dict_with_trains):
                #         if self.dict_with_trains[train_id].is_button_pressed(mouse_pos, i):
                #             button_was_pressed += True
                #             self.current_selected_train_id = train_id
                #     # add trains
                #     if self.current_mode == "trains" and not button_was_pressed:
                #         tile_1, tile_2 = self.map.get_track_by_coord_world(coord_world)
                #         if tile_1 and tile_2:
                #             self.dict_with_trains[self.lowest_free_train_id] = Train(self.map, self.lowest_free_train_id, tile_1, tile_2)
                #             self.lowest_free_train_id += 1
                #             self.map.calculate_trains_path(self.dict_with_trains)
                #     # add targets
                #     if self.current_mode == "targets" and not button_was_pressed and \
                #                 self.current_selected_train_id in self.dict_with_trains:
                #         self.dict_with_trains[self.current_selected_train_id].movement_target.append(current_tile_id)
                #         # calculate trains paths
                #         self.map.calculate_trains_path(self.dict_with_trains)
                    
                #     if not button_was_pressed:
                #         self.left_mouse_button_down = True
                #         self.right_mouse_button_down = False

                # # 3 - right click
                # if event.button == 3:
                #     # remove targets
                #     if self.current_mode == "targets":
                #         if self.current_selected_train_id in self.dict_with_trains and \
                #                 current_tile_id in self.dict_with_trains[self.current_selected_train_id].movement_target:
                #             self.dict_with_trains[self.current_selected_train_id].movement_target.remove(current_tile_id)
                #             # calculate trains paths
                #             self.map.calculate_trains_path(self.dict_with_trains)
                #     # remove trains
                #     if self.current_mode == "trains":
                #         trains_to_del = []
                #         for train_id in self.dict_with_trains:
                #             if self.dict_with_trains[train_id].last_tile_id == current_tile_id \
                #                              or self.dict_with_trains[train_id].tile_id == current_tile_id:
                #                 trains_to_del.append(train_id)
                #         for remove_train_id in trains_to_del:
                #             del self.dict_with_trains[remove_train_id]
                #         self.map.calculate_trains_path(self.dict_with_trains)

                #     else:
                #         self.right_mouse_button_down = True
                #         self.left_mouse_button_down = False
                pass

            # mouse button up
            if event.type == pygame.MOUSEBUTTONUP:
                # 1 - left click
                if event.button == 1:
                    self.left_mouse_button_down = False
                    self.last_used_tile = 0
                    self.current_used_tile = 0

                # 2 - middle click
                if event.button == 2:
                    # define new view center
                    self.offset_horizontal -= (mouse_pos[0] - WIN_WIDTH/2) / self.scale
                    self.offset_vertical -= (mouse_pos[1] - WIN_HEIGHT/2) / self.scale

                # 3 - right click
                if event.button == 3:
                    self.right_mouse_button_down = False
                    self.last_used_tile = 0
                    self.current_used_tile = 0

                # 4 - scroll up
                if event.button == 4:
                    old_scale = self.scale

                    self.scale *= 2
                    if self.scale >= 4: self.scale = 4

                    if old_scale - self.scale:
                        # OFFSET_HORIZONTAL -= mouse_pos[0] / old_scale - WIN_WIDTH/2 / SCALE
                        # OFFSET_VERTICAL -= mouse_pos[1] / old_scale - WIN_HEIGHT/2 / SCALE
                        self.offset_horizontal -= WIN_WIDTH/2 / old_scale - WIN_WIDTH/2 / self.scale
                        self.offset_vertical -= WIN_HEIGHT/2 / old_scale - WIN_HEIGHT/2 / self.scale

                # 5 - scroll down
                if event.button == 5:
                    old_scale = self.scale

                    self.scale /= 2
                    # if SCALE <= 0.25: SCALE = 0.25
                    if self.scale <= 0.125: self.scale = 0.125

                    if old_scale - self.scale:
                        # OFFSET_HORIZONTAL -= mouse_pos[0] / old_scale - WIN_WIDTH/2 / SCALE
                        # OFFSET_VERTICAL -= mouse_pos[1] / old_scale - WIN_HEIGHT/2 / SCALE
                        self.offset_horizontal -= WIN_WIDTH/2 / old_scale - WIN_WIDTH/2 / self.scale
                        self.offset_vertical -= WIN_HEIGHT/2 / old_scale - WIN_HEIGHT/2 / self.scale


            # keys that can be pressed only ones
            if event.type == pygame.KEYDOWN:
                # pause
                if event.key == pygame.K_SPACE:
                    if self.pause: self.pause = False
                    else: self.pause = True
                # center
                if event.key == pygame.K_c:
                    self.scale = 1
                    self.offset_horizontal, self.offset_vertical = 0, 0

    # keys that can be pressed multiple times
        # move
        move_speed = 5 / self.scale
        # move left
        if keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a]:
            self.offset_horizontal += move_speed
        # move right
        if keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]:
            self.offset_horizontal -= move_speed
        # move up
        if keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_w]:
            self.offset_vertical += move_speed
        # move down
        if keys_pressed[pygame.K_DOWN] or keys_pressed[pygame.K_s]:
            self.offset_vertical -= move_speed


    # # handle the remaining logic related to mouse operation
        
    #     # adding entities
    #     if self.left_mouse_button_down and (not current_tile_id or self.last_used_tile != current_tile_id):
    #         # add new tile
    #         if self.current_mode == "terrain":
    #             current_tile_id = self.map.add_tile(coord_id, self.current_terrain)
    #         # add new track
    #         if self.current_mode == "tracks" and self.last_used_tile and current_tile_id:
    #             self.map.add_track(self.last_used_tile, current_tile_id)
    #             self.map.calculate_trains_path(self.dict_with_trains)

    #         self.last_used_tile = current_tile_id
    #     # removing entities
    #     if self.right_mouse_button_down:
    #         # remove tile
    #         if self.current_mode == "terrain" and current_tile_id:
    #             # remove tile from train variables
    #             self.map.remove_tile(current_tile_id)
    #             self.map.calculate_trains_path(self.dict_with_trains)
    #         # remove tracks
    #         if self.current_mode == "tracks" and current_tile_id:
    #             tile_1, tile_2 = self.map.get_track_by_coord_world(coord_world)
    #             if tile_1 and tile_2:
    #                 # remove tile from train variables
    #                 self.map.remove_track(tile_1, tile_2)
    #                 self.map.calculate_trains_path(self.dict_with_trains)
        
    def update(self):
        """Game logic for the scene."""

        # count tics
        self.current_frame += 1
        if self.current_frame == FRAMERATE: # // 10:
            self.current_frame = 0

        # check hovering of the mouse
        mouse_coord = pygame.mouse.get_pos()
        for mode_button in self.list_with_mode_buttons:
            mode_button.check_hovering(mouse_coord)
        if self.current_mode == "terrain":
            for terrain_button in self.list_with_terrain_buttons:
                terrain_button.check_hovering(mouse_coord)

        # # run the simulation
        # if not self.current_frame:
            
        #     # calculate trains free paths
        #     self.map.calculate_trains_path(self.dict_with_trains)

        # # run trains
        # for train_id in self.dict_with_trains:
        #     self.dict_with_trains[train_id].run(self.map, self.dict_with_trains)


    def render(self, win):
        """Draw scene on the screen."""

        # clear screen
        win.fill(BLACK)

        # draw the map
        self.map.draw(win, self.offset_horizontal, self.offset_vertical, self.scale)

        # draw trains buttons
        for i, train_id in enumerate(self.map.dict_with_trains):
            self.map.dict_with_trains[train_id].draw_button(win, i)
            if train_id == self.current_selected_train_id:
                self.map.dict_with_trains[train_id].draw_button_selection(win, i)

        # draw buttons
        for mode_button in self.list_with_mode_buttons:
            mode_button.draw(win)
        if self.current_mode == "terrain":
            for terrain_button in self.list_with_terrain_buttons:
                terrain_button.draw(win)


# ======================================================================


class ConnectionErrorScene(SceneBase):
    def __init__(self):
        """Initialization of the scene."""
        SceneBase.__init__(self)
        self.text = FixText((WIN_WIDTH/2, WIN_HEIGHT/2), "Connection Error. Press any key to close the program.", 20)
    
    def process_input(self, events, keys_pressed):
        """
        Receive all the events that happened since the last frame.
        Handle all received events.
        """
        for event in events:
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                self.terminate()
    
    def update(self):
        """Game logic for the scene."""
        pass

    def render(self, win):
        """Draw scene on the screen."""
        # clear screen
        win.fill(BLACK)
        # print text
        self.text.draw(win)


# ======================================================================


class TemplateScene(SceneBase):
    def __init__(self):
        """Initialization of the scene."""
        SceneBase.__init__(self)
    
    def process_input(self, events, keys_pressed):
        """
        Receive all the events that happened since the last frame.
        Handle all received events.
        """
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                # move to the next scene when the user pressed Enter
                self.switch_scene(GameScene())
        
    def update(self):
        """Game logic for the scene."""
        pass
    
    def render(self, win):
        """Draw scene on the screen."""
        win.fill(HOTPINK)