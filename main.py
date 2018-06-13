
import entities.entity as entities
import environment.environment as Env
import behaviours.behaviour as behaviour

import utils.pathfinding as pf
import utils.utils as utils
import utils.basic_colors as basic_colors
import utils.selectionrect as select_rect

import pygame
import random
import sys
import time
import numpy as np


from screeninfo import get_monitors
monitor = get_monitors()[0]

# main_surface_width, main_surface_height = 860, 680
screen_width, screen_height = int(monitor.width*0.75), int(monitor.height*0.75)

main_surface_width, main_surface_height = int(screen_width*0.75), int(screen_height)

info_surface_width, info_surface_height = int(screen_width*0.25), int(screen_height)


import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % ((monitor.width/2)-(screen_width/2),(monitor.height/2)-(screen_height/2))


from pygame.locals import *

pygame.init()

#Generate zip file for ready-to-use windows app (in root directory) : C:/Python27/Scripts/pyinstaller main.py

def main():
    DISPLAY_DEBUG = False

    env = Env.Environment(main_surface_width, main_surface_height)

    clock = pygame.time.Clock()

    window = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Colony Life Sim")

    screen = pygame.Surface((main_surface_width, main_surface_height))
    alpha_surface = pygame.Surface((main_surface_width, main_surface_height), pygame.SRCALPHA)
    info_surface = pygame.Surface((info_surface_width, info_surface_height), pygame.SRCALPHA)
    
    for i in range(10):
        o = entities.Obstacle(random.randint(30, 100), random.randint(30, 100), env)
        o.setRandomPose(main_surface_width, main_surface_height)
        env.addObstacle(o)
    env.splitEnvironment()
    env.constructGraph(Env.areNeigbhoursSquare)
    env.constructRiver(5)


    l_npc = []
    for i in range(10):
        entity = entities.NPC(env, "entity"+str(i))
        entity.setRandomPose(main_surface_width, main_surface_height)
        entity.setIdleBehaviour()
        l_npc.append(entity)

    l_spawner = []
    for i in range(2):
        spawnerFood = entities.Spawner(env, "spawner"+str(i), "foodspawner", 3, random.randint(540, 620), random.random()*0.6 + 0.8, True)
        spawnerFood.setRandomPose(main_surface_width, main_surface_height)
        spawnerFood.setSpawnerBehaviour()
        for i in range(1):
            spawnerFood.spawn()
        l_spawner.append(spawnerFood)


    run = True

    #Buttons
    color_rect_button = basic_colors.BLUE
    rect_button = pygame.Rect((main_surface_width + 10, main_surface_height*0.94), (info_surface_width*0.25, info_surface_height*0.05))
    
    color_quit_button = basic_colors.RED
    quit_button = pygame.Rect((main_surface_width + info_surface_width*0.65, main_surface_height*0.94), 
                                (info_surface_width*0.25, info_surface_height*0.05))
    


    q_time = []

    selected = []
    selection_on = False
    selection_rect = None

    while run:
        t1 = time.time()

        # clock.tick(60) #tick at 60fps

        t_other = time.time()

        screen.fill(basic_colors.GREEN)
        alpha_surface.fill(basic_colors.EMPTY)
        info_surface.fill(basic_colors.WHITE)

        mp = pygame.mouse.get_pos()

        if quit_button.collidepoint(mp):
            color_quit_button = basic_colors.RED_2
        else:
            color_quit_button = basic_colors.RED

        if rect_button.collidepoint(mp):
            color_rect_button = basic_colors.BLUE_2
        elif DISPLAY_DEBUG:
            color_rect_button = basic_colors.BLUE_3
        else:
            color_rect_button = basic_colors.BLUE

        #Single event control
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE :
                    run = False
                if event.key == K_d:
                    DISPLAY_DEBUG = not DISPLAY_DEBUG
            elif event.type == pygame.MOUSEBUTTONDOWN:
                #LMB
                if event.button == 1:
                    if quit_button.collidepoint(mp):
                        run = False
                        color_quit_button = basic_colors.RED_3
                    elif rect_button.collidepoint(mp):
                        DISPLAY_DEBUG = not DISPLAY_DEBUG

                    if alpha_surface.get_rect().collidepoint(mp) and not selection_on:
                        selection_on = True
                        selection_rect = select_rect.SelectionRect(alpha_surface, event.pos)
                #MMB
                if event.button == 2:
                    pass
                #RMB
                if event.button == 3:
                    if selected:
                        rect = env.getCurrentRect(mp)
                        if rect != None:
                            for e in selected:
                                rect_e = env.getCurrentRect(e.getPose())
                                if rect_e != None:
                                    print pf.getPathLength(env, rect.center, rect_e.center)
                                else:
                                    print "error rect entity not found"
                                if e.behaviour.state == "goto":
                                    e.behaviour.setSpecificTarget(mp)
                                    e.behaviour.computePath()
                                else:
                                    e.setGOTOBehaviour(mp)
                    # rect = env.collideOneObstacle_Point(mp)
                    # if rect != None:
                    #     res = entities.Ressource(env, "food", random.randint(30, 70), False)
                    #     res.setPose(mp[0], mp[1])
                    #     res.setRegrowBehaviour()
                    #     env.addRessource(res)
                    pass
                #Mouth Wheel up
                if event.button == 4:
                    pass
                #Mouth Wheel down
                if event.button == 5:
                    pass
            elif event.type == MOUSEMOTION:
                if selection_on:
                    # update the selection rectangle while the mouse is moving
                    selection_rect.updateRect(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                #LMB
                if event.button == 1:
                    if selection_on:
                        selection_on = False
                        selection_rect.updateRect(event.pos)

                        selected = []
                        for e in l_npc:
                            if selection_rect.collidepoint(e.getPose()):
                                selected.append(e)

                        selection_rect = None
                        print [x.name for x in selected]
                        # print "Final selection rectangle:",selection_rect

        t_other = time.time() - t_other

        #Logic
        #play each entity
        t_update = time.time()
        for e in l_npc:
            #slow as fuck
            e.update()
        for r in l_spawner:
            r.update()
        for kr in env.ressources.keys():
            for r in env.ressources[kr]:
                r.update()
            env.ressources[kr] = [x for x in env.ressources[kr] if not x.dead]
        t_update = time.time() - t_update

        #Remove dead entities
        l_npc = [x for x in l_npc if not x.dead]

        #Display Debug

        t_display = time.time()

        if DISPLAY_DEBUG:
            for k in env.graph.keys():
                for pos in env.graph[k]:
                    # print env.graph[k][pos]/10
                    pygame.draw.line(screen, basic_colors.RED, k, pos, 1)
            for r in env.graph_rect:
                pygame.draw.rect(alpha_surface, basic_colors.ALPHA_WHITE, r, 1)

        #Display

        #Env
        for o in env.obstacles:
            o.sprite.draw(screen)
        for i in range(1, len(env.river_path)):
            pygame.draw.line(screen, basic_colors.BLUE, env.river_path[i-1], env.river_path[i], 5)
        for r in env.saved_rect_from_river:
            pygame.draw.rect(screen, basic_colors.BLUE, r)
            
        #Entities
        for kr in env.ressources.keys():
            for r in env.ressources[kr]:
                r.sprite.draw(screen, alpha_surface)
        for e in l_npc:
            e.sprite.draw(screen)
            if e in selected:
                e.sprite.drawSelected(screen, alpha_surface, basic_colors.RED)
        for sp in l_spawner:
            sp.sprite.draw(screen)
        
        if selection_rect != None and hasattr(selection_rect, "rect"):
            # print selection_rect.rect
            selection_rect.draw(alpha_surface)

        t_display = time.time() - t_display


        #Info surface
        t2 = time.time()
        diff_t = t2 - t1

        fps = round(1.0 / diff_t, 0)
        q_time.append(round(fps))
        if len(q_time) >= 75 : q_time = q_time[1:]

        #info text
        fontsize = int(info_surface_height*0.02)
        font = pygame.font.SysFont('Sans', fontsize)

        text = str(round(np.mean(q_time))) + " fps / 1 frame : " +  str(round(diff_t, 3)) + "s"
        text2 = str(round((round(t_update, 4) / diff_t)*100)) + "% logic, " + str(round((round(t_display, 4) / diff_t)*100)) + "% disp, " + str(round((round(t_other, 4) / diff_t)*100)) + "% otr"
        text3 = "Selected Entities :"
        displ_text = font.render(text, True, basic_colors.BLACK)
        displ_text2 = font.render(text2, True, basic_colors.BLACK)
        displ_text3 = font.render(text3, True, basic_colors.BLACK)
        info_surface.blit(displ_text, (10, 10))
        shift = 10
        info_surface.blit(displ_text2, (10, 10 + shift))
        shift = 10 + shift
        info_surface.blit(displ_text3, (10, 20 + shift))
        shift = 20 + shift

        for e in selected:
            txt_basic = e.name + " (" + str(round(e.pose.x, 2)) + ", " + str(round(e.pose.y, 2)) + ")"
            displ_txt_basic = font.render(txt_basic, True, basic_colors.BLACK)

            txt_hunger = "     hunger : " + str(e.hunger) + "/" + str(e.hunger_max) + " (" + str(e.hunger_thresh) + ")"
            displ_txt_hunger = font.render(txt_hunger, True, basic_colors.BLACK)

            txt_behaviour = "     state : " + e.behaviour.state
            displ_txt_behaviour = font.render(txt_behaviour, True, basic_colors.BLACK)

            info_surface.blit(displ_txt_basic, (10, shift + fontsize + 2))
            shift = shift + fontsize + 2
            info_surface.blit(displ_txt_hunger, (10, shift + fontsize))
            shift = shift + fontsize
            info_surface.blit(displ_txt_behaviour, (10, shift + fontsize))
            shift = shift + fontsize

            for k in e.bagpack:
                txt_bagpack = "          " + k + " : " + str(round(e.bagpack[k], 2))
                displ_txt_bp = font.render(txt_bagpack, True, basic_colors.BLACK)

                info_surface.blit(displ_txt_bp, (10, shift + fontsize))
                shift = shift + fontsize


        #buttons
        fontsize = int(info_surface_height*0.02)
        font = pygame.font.SysFont('Sans', fontsize)

        quit_text = font.render("Quit (Esc)", True, basic_colors.BLACK)

        rect_text = font.render("Rect (d)", True, basic_colors.BLACK)

        #Blit and Flip surfaces
        window.blit(screen, (0, 0))
        window.blit(alpha_surface, (0, 0))
        window.blit(info_surface, (main_surface_width, 0))

        pygame.draw.rect(window, color_quit_button, quit_button)
        window.blit(quit_text, (quit_button.center[0] - (quit_text.get_width()/2), 
            quit_button.center[1] - (quit_text.get_height()/2)))

        pygame.draw.rect(window, color_rect_button, rect_button)
        window.blit(rect_text, (rect_button.center[0] - (rect_text.get_width()/2), 
            rect_button.center[1] - (rect_text.get_height()/2)))

        pygame.display.flip()

    for e in l_npc:
        e.die()
        e.update()

    for kr in env.ressources.keys():
        for r in env.ressources[kr]:
            r.die()
            r.update()

    print("End !")


if __name__ == '__main__':
    main()