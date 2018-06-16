#!/usr/bin/env python
#-*- coding: utf-8 -*-

from __future__ import print_function

import entities.entity as entities
import environment.environment as Env
import behaviours.behaviour as behaviour

import utils.pathfinding as pf
import utils.utils as utils
import utils.basic_colors as basic_colors
import utils.selectionrect as select_rect

import profilerConfig as pc

import pygame
import random
import sys
import time
import numpy as np
import copy
from screeninfo import get_monitors
import os
from pygame.locals import *
import threading


#Generate zip file for ready-to-use windows app (in root directory) : pyinstaller -F colonylife.py

class DisplayLoadingThread(threading.Thread):
    def __init__(self):
        super(DisplayLoadingThread, self).__init__()
    
        monitor = get_monitors()[0]
        
        pygame.init()

        screen_width, screen_height = int(monitor.width*0.30), int(monitor.height*0.30)
        self.window = pygame.display.set_mode((screen_width, screen_height))
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % ((monitor.width/2)-(screen_width/2),(monitor.height/2)-(screen_height/2))


        self.is_running = True

    def run(self):
        while self.is_running:

            self.window.fill(basic_colors.BLACK)

            fontsize = int(self.window.get_height()*0.2)
            font = pygame.font.SysFont('Sans', fontsize)

            text1 = font.render("Loading...", True, basic_colors.WHITE)
            self.window.blit(text1, (self.window.get_rect().center[0] - (text1.get_width()/2),
                            self.window.get_height()/4 ) )

            fontsize2 = int(self.window.get_height()*0.15)
            font2 = pygame.font.SysFont('Sans', fontsize2)

            text2 = font2.render(pc.get("ENV_CONSTR_TRACK")["scope"], True, basic_colors.WHITE)
            self.window.blit(text2, (self.window.get_rect().center[0] - (text2.get_width()/2), 
                            int(self.window.get_height()*0.5) ) )

            fontsize3 = int(self.window.get_height()*0.12)
            font3 = pygame.font.SysFont('Sans', fontsize3)

            text3 = font3.render("{}%".format(pc.get("ENV_CONSTR_TRACK")["percent"]), True, basic_colors.WHITE)
            self.window.blit(text3, (self.window.get_rect().center[0] - (text3.get_width()/2), 
                            int(self.window.get_height()*0.65) ) )

            pygame.display.flip()


    def stop(self):
        self.is_running = False
        pass
        # self._stopper.set()
        
    def stopped(self):
        pass
        # return self._stopper.isSet()

        

def main(nb_npc=10, nb_obs=10, nb_spawner=2, _profiler=-1, DISPLAY=True, debug_displ=False, number=0, max_number=0):

    tinit = time.time()

    #FIRST INIT
    monitor = get_monitors()[0]
        
    # main_surface_width, main_surface_height = 860, 680
    screen_width, screen_height = int(monitor.width*0.75), int(monitor.height*0.75)
    main_surface_width, main_surface_height = int(screen_width*0.75), int(screen_height)
    info_surface_width, info_surface_height = int(screen_width*0.25), int(screen_height)
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % ((monitor.width/2)-(screen_width/2),(monitor.height/2)-(screen_height/2))
    
    #LOADING
    env = Env.Environment(main_surface_width, main_surface_height)
    
    thread_loading = DisplayLoadingThread()

    thread_loading.start()

    for i in range(nb_obs):
        o = entities.Obstacle(random.randint(30, 100), random.randint(30, 100), env)
        o.setRandomPose(main_surface_width, main_surface_height)
        env.addObstacle(o)

    env.constructEnvironment(5)

    time.sleep(1)

    thread_loading.stop()
    thread_loading.join()



    DISPLAY_DEBUG = debug_displ

    pygame.init()

    PROFIL = _profiler != -1
    curr_profiler = 0

    clock = pygame.time.Clock()

    if DISPLAY:

        window = pygame.display.set_mode((screen_width, screen_height))
        caption = "Colony Life Simulation" + ("" if not PROFIL else " : Profiler n° {0}/{1}".format(number+1, max_number))
        pygame.display.set_caption(caption)

        topleft_screen = (0, 0)
        screen = pygame.Surface((main_surface_width, main_surface_height))
        topleft_alpha_surface = topleft_screen
        alpha_surface = pygame.Surface((main_surface_width, main_surface_height), pygame.SRCALPHA)
        topleft_info = (topleft_screen[0]+main_surface_width, 0)
        info_surface = pygame.Surface((info_surface_width, info_surface_height), pygame.SRCALPHA)

    l_npc = []
    for i in range(nb_npc):
        entity = entities.NPC(env, "entity"+str(i))
        entity.setRandomPose(main_surface_width, main_surface_height)
        entity.setIdleBehaviour()
        l_npc.append(entity)

    l_spawner = []
    for i in range(nb_spawner):
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

    color_pause_button = basic_colors.OLIVE
    pause_button = pygame.Rect((main_surface_width + info_surface_width*0.35, main_surface_height*0.94), 
                                (info_surface_width*0.25, info_surface_height*0.05))

    color_info_button = basic_colors.YELLOW
    info_button = pygame.Rect((main_surface_width + 10, main_surface_height*0.84), 
                                (info_surface_width*0.25, info_surface_height*0.05))
    
    q_time = []

    selected_npc = []
    selection_on = False
    selection_rect = None

    paused = False
    info = False

    shift_list_ent_span = 4
    shift_list_ent_inf = 0
    shift_list_ent_sup = shift_list_ent_span

    tinit = time.time() - tinit
    pc.set("TIME_INIT", tinit)

    t_loop = 0.1

    t_update_list = []
    t_display_list = []
    t_other_list = []

    #Start Threads
    [x.start() for x in l_npc]
    [x.start() for x in l_spawner]
    # for kr in env.ressources.keys():
    #     for r in env.ressources[kr]:
    #         r.start()

    def handle_pause(paused):
        if paused:
            for e in l_npc:
                e.pause()
            for r in l_spawner:
                r.pause()
            for kr in env.ressources.keys():
                for r in env.ressources[kr]:
                    r.pause()
        else:
            for e in l_npc:
                e.resume()
            for r in l_spawner:
                r.resume()
            for kr in env.ressources.keys():
                for r in env.ressources[kr]:
                    r.resume()

    while run:

        t1 = time.time()
        if PROFIL:
            T_TOTAL = time.time()

            if curr_profiler%500 == 0:
                pc.append_to("NB_NPC", len(l_npc))
            curr_profiler += 1
            if curr_profiler%10 == 0:
                print(str(round(float(curr_profiler)/float(_profiler) * 100)) + "% (" + str(curr_profiler) + "/" + str(_profiler) + ")", end='\r')
            if curr_profiler >= _profiler:
                print ("End because profiler finished")
                run = False
        


        # clock.tick(120) #tick at 120fps

        t_other = time.time()
        if DISPLAY:
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

        if pause_button.collidepoint(mp):
            color_pause_button = basic_colors.OLIVE_3
        elif paused:
            color_pause_button = basic_colors.OLIVE_2
        else:
            color_pause_button = basic_colors.OLIVE

        if info_button.collidepoint(mp):
            color_info_button = basic_colors.YELLOW_3
        elif info:
            color_info_button = basic_colors.YELLOW_2
        else:
            color_info_button = basic_colors.YELLOW


        #Single event control
        if not PROFIL:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == K_ESCAPE :
                        run = False
                    elif event.key == K_d:
                        DISPLAY_DEBUG = not DISPLAY_DEBUG
                    elif event.key == K_i:
                        info = not info
                    elif event.key == K_SPACE:
                        paused = not paused
                        handle_pause(paused)
                    elif event.key == pygame.K_a and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        for e in l_npc:
                            e.selected_npc = True
                        selected_npc = l_npc
                        shift_list_ent_inf = 0
                        shift_list_ent_sup = shift_list_ent_span
                    elif event.key == pygame.K_r and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        for e in l_npc:
                            e.selected_npc = True
                        selected_npc = copy.copy(l_npc)
                        np.random.shuffle(selected_npc)
                        selected_npc = selected_npc[:shift_list_ent_span]

                        shift_list_ent_inf = 0
                        shift_list_ent_sup = shift_list_ent_span
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    #LMB
                    if event.button == 1:
                        if quit_button.collidepoint(mp):
                            run = False
                            color_quit_button = basic_colors.RED_3
                        elif rect_button.collidepoint(mp):
                            DISPLAY_DEBUG = not DISPLAY_DEBUG
                        elif pause_button.collidepoint(mp):
                            paused = not paused
                            handle_pause(paused)  
                        elif info_button.collidepoint(mp):
                            info = not info

                        if alpha_surface.get_rect(topleft=topleft_alpha_surface).collidepoint(mp) and not selection_on:
                            selection_on = True
                            selection_rect = select_rect.SelectionRect(alpha_surface, event.pos)
                    #MMB
                    if event.button == 2:
                        pass
                    #RMB
                    if event.button == 3:
                        if selected_npc:
                            rect = env.getCurrentRect(mp)
                            if rect != None:
                                for e in selected_npc:
                                    rect_e = env.getCurrentRect(e.getPose())
                                    if e.behaviour.state == "goto":
                                        e.behaviour.setSpecificTarget(mp)
                                        e.behaviour.computePath()
                                    else:
                                        e.setGOTOBehaviour(mp)
                    #Mouth Wheel up
                    if event.button == 4:
                        if info_surface.get_rect(topleft=topleft_info).collidepoint(mp):
                            shift_list_ent_inf = shift_list_ent_inf-1 if shift_list_ent_inf>0 else 0
                            shift_list_ent_sup = shift_list_ent_sup-1 if shift_list_ent_sup>shift_list_ent_span else shift_list_ent_span
                    #Mouth Wheel down
                    if event.button == 5:
                        if info_surface.get_rect(topleft=topleft_info).collidepoint(mp):
                            shift_list_ent_inf = shift_list_ent_inf+1 if shift_list_ent_inf<(len(selected_npc)-shift_list_ent_span) else len(selected_npc)-shift_list_ent_span
                            shift_list_ent_sup = shift_list_ent_sup+1 if shift_list_ent_sup<len(selected_npc) else len(selected_npc)
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

                            for e in selected_npc:
                                e.selected_npc = False
                            selected_npc = []
                            for e in l_npc:
                                if selection_rect.colliderect(e.sprite.rect):
                                    e.selected_npc = True
                                    selected_npc.append(e)
                            shift_list_ent_inf = 0
                            shift_list_ent_sup = shift_list_ent_span

                            selection_rect = None
                            # print [x.name for x in selected_npc]

        t_other = time.time() - t_other
        t_other_list.append(t_other)
        if len(t_other_list) > 100:
            t_other_list = t_other_list[1:]

        t_update = time.time()
        if PROFIL:
            T_LOGIC = time.time()

        # if not paused:
        #     #Logic
        #     #play each entity
        #     for e in l_npc:
        #         #slow as fuck
        #         e.update()
        #     for r in l_spawner:
        #         r.update()
            # for kr in env.ressources.keys():
        #         for r in env.ressources[kr]:
        #             r.update()
        #         env.ressources[kr] = [x for x in env.ressources[kr] if not x.dead]

        #Remove dead entities            
        for kr in env.ressources.keys():
            for deadres in [x for x in env.ressources[kr] if x.dead]:
                deadres.join()
            env.ressources[kr] = [x for x in env.ressources[kr] if not x.dead]

        for deadnpc in [x for x in l_npc if x.dead]:
            deadnpc.join()
        l_npc = [x for x in l_npc if not x.dead]

        t_update = time.time() - t_update
        t_update_list.append(t_update)
        if len(t_update_list) > 100:
            t_update_list = t_update_list[1:]
        if PROFIL:
            T_LOGIC = time.time() - T_LOGIC
            pc.append_to("TIME_LOGIC", T_LOGIC)


        #Display Debug
        if PROFIL:
            T_DISPLAY = time.time()

        if DISPLAY:
            t_display = time.time()

            if DISPLAY_DEBUG:
                for k in env.graph.keys():
                    for pos in env.graph[k]:
                        # print env.graph[k][pos]/10
                        pygame.draw.line(screen, basic_colors.RED, k, pos, 1)
                for r in env.graph_rect:
                    pygame.draw.rect(alpha_surface, basic_colors.ALPHA_WHITE, r, 1)
                for ro in env.obstacles_rect:
                    pygame.draw.rect(alpha_surface, basic_colors.ALPHA_MAGENTA, ro, 1)
                for rv in env.saved_rect_from_river:
                    pygame.draw.rect(alpha_surface, basic_colors.ALPHA_CYAN, rv, 1)


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
                    r.sprite.draw(screen, alpha_surface, info)
            for e in l_npc:
                e.sprite.draw(screen, False)
                if e in selected_npc:
                    e.sprite.drawSelected(screen, alpha_surface, basic_colors.RED)
            for sp in l_spawner:
                sp.sprite.draw(screen, info)
            
            if selection_rect != None and hasattr(selection_rect, "rect"):
                # print selection_rect.rect
                selection_rect.draw(alpha_surface)

            t_display = time.time() - t_display
            t_display_list.append(t_display)
            if len(t_display_list) > 100:
                t_display_list = t_display_list[1:]


            #Info surface
            t2 = time.time()
            diff_t = (t2 - t1) if (t2 - t1) > 0 else 0.0001

            fps = round(1.0 / t_loop, 0)
            q_time.append(round(fps))
            if len(q_time) >= 50 : q_time = q_time[1:]

            #info text
            fontsize = int(info_surface_height*0.02)
            font = pygame.font.SysFont('Sans', fontsize)

            # print('> Results aggregation [{0:{2}d}/{1}]'.format(i+1, n_files , len_files), end='\r')

            # text = str(round(np.mean(q_time))) + " fps (" +  str(round(diff_t, 3)) + "s)"
            tmp = int(round(np.mean(q_time)))
            pc.set("FORCED_FPS", tmp)
            text = "{0:03d} LPS (~{1:.4f}s/loop)".format(tmp, round(diff_t, 4))#, len(str(tmp)) - len(str(int(tmp))) - 2 )
            if paused:
                text += " PAUSED"
            # text2 = str(round((round(t_update, 4) / diff_t)*100)) + "% logic, " + str(round((round(t_display, 4) / diff_t)*100)) + "% disp, " + str(round((round(t_other, 4) / diff_t)*100)) + "% otr"
            text2 = "{0:03d}% logic, {1:03d}% display, {2:03d}% other".format(int(round((round(t_update, 4) / diff_t)*100)), int(round((round(t_display, 4) / diff_t)*100)), int(round((round(t_other, 4) / diff_t)*100)))
            text3 = "Selected Entities ({0}/{1}) :".format(str(len(selected_npc)), str(len(l_npc)))
            displ_text = font.render(text, True, basic_colors.BLACK)
            displ_text2 = font.render(text2, True, basic_colors.BLACK)
            displ_text3 = font.render(text3, True, basic_colors.BLACK)
            info_surface.blit(displ_text, (10, 10))
            shift = 10
            info_surface.blit(displ_text2, (10, 10 + shift))
            shift = 10 + shift
            info_surface.blit(displ_text3, (10, 20 + shift))
            shift = 20 + shift


            # print (shift_list_ent_inf, shift_list_ent_sup)
            if shift_list_ent_inf > 0:
                txt_dotdotdot = "..."
                displ_dotdotdot = font.render(txt_dotdotdot, True, basic_colors.BLACK)
                info_surface.blit(displ_dotdotdot, (10, shift + fontsize + 2))
                shift = shift + fontsize + 2

            for e in selected_npc[shift_list_ent_inf:shift_list_ent_sup]:
                txt_basic = e.name + " (" + str(round(e.pose.x, 2)) + ", " + str(round(e.pose.y, 2)) + ")"
                displ_txt_basic = font.render(txt_basic, True, basic_colors.BLACK)

                txt_stat1 = "     speed : " + str(e.speed)
                displ_txt_stat1 = font.render(txt_stat1, True, basic_colors.BLACK)

                txt_hunger = "     hunger : " + str(e.hunger)  + " (have to eat ? " + str(e.have_to_eat) + ")"
                displ_txt_hunger = font.render(txt_hunger, True, basic_colors.BLACK)

                txt_behaviour = "     state : " + (e.behaviour.state if e.behaviour != None else "none")
                displ_txt_behaviour = font.render(txt_behaviour, True, basic_colors.BLACK)

                info_surface.blit(displ_txt_basic, (10, shift + fontsize + 2))
                shift = shift + fontsize + 2
                info_surface.blit(displ_txt_stat1, (10, shift + fontsize))
                shift = shift + fontsize
                info_surface.blit(displ_txt_hunger, (10, shift + fontsize))
                shift = shift + fontsize
                info_surface.blit(displ_txt_behaviour, (10, shift + fontsize))
                shift = shift + fontsize

                for k in e.bagpack:
                    txt_bagpack = "          " + k + " : " + str(round(e.bagpack[k], 2))
                    displ_txt_bp = font.render(txt_bagpack, True, basic_colors.BLACK)

                    info_surface.blit(displ_txt_bp, (10, shift + fontsize))
                    shift = shift + fontsize

            if shift_list_ent_sup < len(selected_npc):
                txt_dotdotdot = "..."
                displ_dotdotdot = font.render(txt_dotdotdot, True, basic_colors.BLACK)
                info_surface.blit(displ_dotdotdot, (10, shift + fontsize + 2))
                shift = shift + fontsize + 2


            #buttons
            fontsize = int(info_surface_height*0.02)
            font = pygame.font.SysFont('Sans', fontsize)

            quit_text   = font.render("Quit (Esc)", True, basic_colors.BLACK)

            rect_text   = font.render("Rect (D)", True, basic_colors.BLACK)

            paused_text = font.render("Pause (Spc)", True, basic_colors.BLACK)

            info_text = font.render("Info (I)", True, basic_colors.BLACK)

            #Blit and Flip surfaces
            window.blit(screen, (0, 0))
            window.blit(alpha_surface, (0, 0))
            window.blit(info_surface, (main_surface_width, 0))

            pygame.draw.rect(window, color_quit_button, quit_button)
            window.blit(quit_text, (quit_button.center[0] - (quit_text.get_width()/2), 
                quit_button.center[1] - (quit_text.get_height()/2) ) )

            pygame.draw.rect(window, color_rect_button, rect_button)
            window.blit(rect_text, (rect_button.center[0] - (rect_text.get_width()/2), 
                rect_button.center[1] - (rect_text.get_height()/2) ))

            pygame.draw.rect(window, color_pause_button, pause_button)
            window.blit(paused_text, (pause_button.center[0] - (paused_text.get_width()/2), 
                pause_button.center[1] - (paused_text.get_height()/2) ) )

            pygame.draw.rect(window, color_info_button, info_button)
            window.blit(info_text, (info_button.center[0] - (info_text.get_width()/2), 
                info_button.center[1] - (info_text.get_height()/2) ) )

            pygame.display.flip()

        if PROFIL:
            T_DISPLAY = time.time() - T_DISPLAY
            pc.append_to("TIME_DISPLAY", T_DISPLAY)

            T_TOTAL = time.time() - T_TOTAL
            pc.append_to("TIME_TOTAL", T_TOTAL)
        t_loop = time.time() - t1

        # min_time_loop = 0.002
        # if t_loop < min_time_loop:
        #     time.sleep(min_time_loop - t_loop)
        #     t_loop = min_time_loop
        #     print("sleep for {}".format(min_time_loop-t_loop))

    for e in l_npc:
        e.die()
        e.update()
        e.join()

    for sp in l_spawner:
        sp.die()
        sp.join()

    for kr in env.ressources.keys():
        for r in env.ressources[kr]:
            r.die()
            r.update()
            r.join( )

    print("End !")


if __name__ == '__main__':
    main(nb_npc=80, nb_obs=10, nb_spawner=6, _profiler=-1, DISPLAY=True, debug_displ=False)