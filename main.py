# Trains 2024
# By Tomasz Golaszewski
# 07.2024

# 

import pygame
import os
from sys import path

# check the system and add files to path
if os.name == "posix":
    path.append('./src')
    print("Linux")
elif os.name == "nt":
    path.append('.\\src')
    print("Windows")
else:
    path.append('.\\src')
    print("other")

from settings import *
from global_variables import *
from classes_scenes import *
from classes_scenes_features import *


def run():
    """main function - runs the game"""
    
    # initialize the pygame
    pygame.init()

    # set window title bar
    pygame.display.set_caption("Tomasz Empire 20022")
    icon_img = pygame.image.load(os.path.join(*ICON_PATH))
    pygame.display.set_icon(icon_img)

    # create the window
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    active_scene = TitleScene()
    current_frame = 0
    current_fps = 0
    fps_text = DynamicText((50, 20), "FPS: %.2f" % FRAMERATE, 20)

    # main loop
    while active_scene != None:
        # control fps
        clock.tick(FRAMERATE)
        current_frame += 1
        if current_frame == FRAMERATE:
            current_frame = 0
            
            # print infos about fps and time
            current_fps = clock.get_fps()
            fps_text.set_text("FPS: %.2f" % current_fps)
            seconds_from_start = pygame.time.get_ticks() // 1000
            minuts_from_start = seconds_from_start // 60
            print()
            print("FPS: %.2f" % current_fps, end="\t")
            print("TIME: " + str(seconds_from_start) + "s (" + str(minuts_from_start) + "min)" )
        
        # event filtering
        keys_pressed = pygame.key.get_pressed()
        filtered_events = []
        for event in pygame.event.get():
            quit_attempt = False
            if event.type == pygame.QUIT:
                quit_attempt = True
            elif event.type == pygame.KEYDOWN:
                alt_pressed = keys_pressed[pygame.K_LALT] or \
                              keys_pressed[pygame.K_RALT]
                if event.key == pygame.K_ESCAPE:
                    quit_attempt = True
                elif event.key == pygame.K_F4 and alt_pressed:
                    quit_attempt = True
            
            if quit_attempt:
                active_scene.terminate()
            else:
                filtered_events.append(event)
        
        # handling events, mouse and keyboard
        active_scene.process_input(filtered_events, keys_pressed)

        # run simulation
        active_scene.update()

        # draw scene on the screen
        active_scene.render(win)
        
        # jump to next scene (or to self)
        active_scene = active_scene.next
        
        # draw FPS  
        fps_text.draw(win)   

        # flip the screen
        pygame.display.flip()


if __name__ == "__main__":
    run()
