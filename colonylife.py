#!/usr/bin/env python
#-*- coding: utf-8 -*-

from __future__ import print_function

import entities.entity as entities
import entities.computationthread as ct
import environment.environment as Env
import environment.positionnalgridoverlay as pgo
import behaviours.behaviour as behaviour

import utils.pathfinding as pf
import utils.utils as utils
import utils.basic_colors as basic_colors
import utils.selectionrect as select_rect
import sprites.sprite as sprite

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


#Generate zip file for ready-to-use windows app (in root directory) : pyinstaller -F -y colonylife.py

class InitialisationScreen(threading.Thread):
    def __init__(self):
        super(InitialisationScreen, self).__init__()
    
        self.daemon = False

        monitor = get_monitors()[0]
        
        pygame.init()

        screen_width, screen_height = int(monitor.width*0.9), int(monitor.height*0.9)
        self.window = pygame.display.set_mode((screen_width, screen_height))
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % ((monitor.width/2)-(screen_width/2),(monitor.height/2)-(screen_height/2))
        
        self.is_running = True

        self.nb_npc = 20 
        self.nb_obs = 5
        self.nb_spawner = 4

    def run(self):
        while self.is_running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == K_ESCAPE :
                        self.is_running = False

            self.window.fill(basic_colors.BLACK)

            fontsize = int(self.window.get_height()*0.2)
            font = pygame.font.SysFont('Sans', fontsize)

            text1 = font.render("Colony Life Simulator", True, basic_colors.WHITE)
            self.window.blit(text1, (self.window.get_rect().center[0] - (text1.get_width()/2),
                            self.window.get_height()*0.12 ) )

            pygame.display.flip()


        # print ("begin main")
        # main(nb_npc=self.nb_npc, nb_obs=self.nb_obs, nb_spawner=self.nb_spawner, _profiler=-1, DISPLAY=True, debug_displ=False)

    def stop(self):
        self.is_running = False
        print("stop Initialisation display")

    def join(self, timeout):
        print("join Initialisation display")
        super(InitialisationScreen, self).join(timeout)

class DisplayLoadingThread(threading.Thread):
    def __init__(self):
        super(DisplayLoadingThread, self).__init__()
    
        self.daemon = True

        monitor = get_monitors()[0]
        
        pygame.init()

        screen_width, screen_height = int(monitor.width*0.9), int(monitor.height*0.9)
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
                            self.window.get_height()*0.17 ) )

            fontsize2 = int(self.window.get_height()*0.12)
            font2 = pygame.font.SysFont('Sans', fontsize2)

            text2 = font2.render(pc.get("ENV_CONSTR_TRACK")["scope"], True, basic_colors.WHITE)
            self.window.blit(text2, (self.window.get_rect().center[0] - (text2.get_width()/2), 
                            int(self.window.get_height()*0.4) ) )


            max_load_rect = self.window.get_rect().width * 0.8
            rect_load = pygame.Rect((self.window.get_rect().width*0.1, self.window.get_rect().height*0.7), (max_load_rect, 70))
            rect_load_current = pygame.Rect((self.window.get_rect().width*0.1, self.window.get_rect().height*0.7), (int(max_load_rect*(pc.get("ENV_CONSTR_TRACK")["percent"]/100)), 70))
            
            fontsize3 = int(self.window.get_height()*0.05)
            font3 = pygame.font.SysFont('Sans', fontsize3)

            pygame.draw.rect(self.window, basic_colors.WHITE, rect_load.inflate(5, 5), 5)
            pygame.draw.rect(self.window, basic_colors.GREEN, rect_load_current)
            
            text3 = font3.render("{}%".format(pc.get("ENV_CONSTR_TRACK")["percent"]), True, basic_colors.WHITE)
            self.window.blit(text3, (rect_load.center[0] - (text3.get_width()/2), 
                            rect_load.center[1] - (text3.get_height()/2) ) )

            pygame.display.flip()


    def stop(self):
        self.is_running = False
        print("stop Loading display")
        # self._stopper.set()

    def join(self, timeout):
        print("join Loading display")
        super(DisplayLoadingThread, self).join(timeout)

class QuitScreenThead(threading.Thread):        
    def __init__(self, timeout=2):
        super(QuitScreenThead, self).__init__()
    
        self.daemon = True
        self.timeout = timeout

        monitor = get_monitors()[0]
        
        pygame.init()

        screen_width, screen_height = int(monitor.width*0.9), int(monitor.height*0.9)
        self.window = pygame.display.set_mode((screen_width, screen_height))
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % ((monitor.width/2)-(screen_width/2),(monitor.height/2)-(screen_height/2))

        self.is_running = True

    def run(self):
        while self.is_running:
            self.window.fill(basic_colors.BLACK)

            fontsize = int(self.window.get_height()*0.2)
            font = pygame.font.SysFont('Sans', fontsize)

            text1 = font.render("Quitting...", True, basic_colors.WHITE)
            self.window.blit(text1, (self.window.get_rect().center[0] - (text1.get_width()/2),
                            self.window.get_height()*0.17 ) )

            fontsize2 = int(self.window.get_height()*0.12)
            font2 = pygame.font.SysFont('Sans', fontsize2)

            text2 = font2.render(pc.get("CURRENT_QUIT_THREAD_NAME"), True, basic_colors.WHITE)
            self.window.blit(text2, (self.window.get_rect().center[0] - (text2.get_width()/2), 
                            int(self.window.get_height()*0.4) ) )


            max_load_rect = self.window.get_rect().width * 0.8
            rect_load = pygame.Rect((self.window.get_rect().width*0.1, self.window.get_rect().height*0.7), (max_load_rect, 70))
            rect_load_current = pygame.Rect((self.window.get_rect().width*0.1, self.window.get_rect().height*0.7), (int(max_load_rect*(float(pc.get("CURRENT_QUITTING_THREAD"))/float(pc.get("TOTAL_QUITTING_THREAD")))), 70))
            
            fontsize3 = int(self.window.get_height()*0.05)
            font3 = pygame.font.SysFont('Sans', fontsize3)

            pygame.draw.rect(self.window, basic_colors.WHITE, rect_load.inflate(5, 5), 5)
            pygame.draw.rect(self.window, basic_colors.RED, rect_load_current)
            
            text3 = font3.render("{}%".format(round((float(pc.get("CURRENT_QUITTING_THREAD"))/float(pc.get("TOTAL_QUITTING_THREAD")))*100), 2), True, basic_colors.WHITE)
            self.window.blit(text3, (rect_load.center[0] - (text3.get_width()/2), 
                            rect_load.center[1] - (text3.get_height()/2) ) )

            pygame.display.flip()

    def stop(self):
        print("stop Quit display")
        self.is_running = False

    def join(self):
        print("join Quit display")
        super(QuitScreenThead, self).join(self.timeout)


def draw_button(surface, fill_color, outline_color, rect, border=1):
    surface.fill(outline_color, rect)
    surface.fill(fill_color, rect.inflate(-border*2, -border*2))   

def main(nb_npc=20, nb_obs=10, nb_spawner=4, _profiler=-1, DISPLAY=True, debug_displ=False, number=0, max_number=0):

    tinit = time.time()
    pygame.init()

    #FIRST INIT
    monitor = get_monitors()[0]
        
    # main_surface_width, main_surface_height = 860, 680
    screen_width, screen_height = int(monitor.width*0.9), int(monitor.height*0.9)
    main_surface_width, main_surface_height = int(screen_width*0.75), int(screen_height)
    info_surface_width, info_surface_height = int(screen_width*0.25), int(screen_height)
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % ((monitor.width/2)-(screen_width/2),(monitor.height/2)-(screen_height/2))
    
    #Init screen
    PROFIL = _profiler != -1

    window = pygame.display.set_mode((screen_width, screen_height))
    caption = "Colony Life Simulation" + ("" if not PROFIL else " : Profiler n° {0}/{1}".format(number+1, max_number))
    pygame.display.set_caption(caption)


    run = True
    run_init = True
    """
    fontsize = int(window.get_height()*0.06)
    font = pygame.font.SysFont('Sans', fontsize)    
    nbNPCtxt = str(nb_npc)
    nbNPCDispl = font.render(nbNPCtxt, True, basic_colors.WHITE)

    nbObsDispl = font.render(str(nb_obs), True, basic_colors.WHITE)

    nbNPCLabelDispl = font.render("Nb NPC :", True, basic_colors.WHITE)

    offset_row1 = int(window.get_rect().width*0.16)
    plus_nbnpc_butt_color = basic_colors.BLUE
    plus_nbnpc_butt = pygame.Rect((offset_row1 + nbNPCDispl.get_rect().width + 10, window.get_rect().height*0.55), 
                                    (window.get_rect().width*0.03, window.get_rect().height*0.035))

    minus_nbnpc_butt_color = basic_colors.RED
    minus_nbnpc_butt = pygame.Rect((offset_row1 + nbNPCDispl.get_rect().width + 10, window.get_rect().height*0.55 + plus_nbnpc_butt.height), 
                                    (window.get_rect().width*0.03, window.get_rect().height*0.035))
    offset_row1 = offset_row1 + plus_nbnpc_butt.width + nbNPCDispl.get_rect().width + 10

    nbObsLabelDispl = font.render("Nb Obs :", True, basic_colors.WHITE)
    plus_nbobs_butt_color = basic_colors.BLUE
    plus_nbobs_butt = pygame.Rect((offset_row1 + nbObsDispl.get_rect().width + 10, window.get_rect().height*0.55), 
                                    (window.get_rect().width*0.03, window.get_rect().height*0.035))

    minus_nbobs_butt_color = basic_colors.RED
    minus_nbobs_butt = pygame.Rect((offset_row1 + nbObsDispl.get_rect().width + 10, window.get_rect().height*0.55 + plus_nbnpc_butt.height), 
                                    (window.get_rect().width*0.03, window.get_rect().height*0.035))
    offset_row1 = offset_row1 + plus_nbnpc_butt.width + nbObsDispl.get_rect().width + 10

    while run_init:
        window.fill(basic_colors.BLACK)

        mp = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == K_RETURN :
                    run_init = False
                elif event.key == K_ESCAPE:
                    run_init = False
                    run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                #LMB
                if event.button == 1:
                    if plus_nbnpc_butt.collidepoint(mp):
                        nb_npc += 1
                    if minus_nbnpc_butt.collidepoint(mp):
                        nb_npc = max(nb_npc - 1, 0)
                    if plus_nbobs_butt.collidepoint(mp):
                        nb_obs += 1
                    if minus_nbobs_butt.collidepoint(mp):
                        nb_obs = max(nb_obs - 1, 0)

        fontsize = int(window.get_height()*0.06)
        font = pygame.font.SysFont('Sans', fontsize)

        nbNPCtxt = str(nb_npc)
        nbNPCDispl = font.render(nbNPCtxt, True, basic_colors.WHITE)
        window.blit(nbNPCLabelDispl, (int(window.get_rect().width*0.03),
                                 int(window.get_height()*0.55)   ))
        window.blit(nbNPCDispl, (int(nbNPCLabelDispl.get_rect().width + nbNPCLabelDispl.get_rect().left + 50),
                                 int(window.get_height()*0.55)   ))

        nbObstxt = str(nb_obs)
        nbObsDispl = font.render(nbNPCtxt, True, basic_colors.WHITE)
        window.blit(nbObsLabelDispl, (int(window.get_rect().width*0.20),
                                 int(window.get_height()*0.55)   ))
        window.blit(nbObsDispl, (int(nbObsLabelDispl.get_rect().width + nbObsLabelDispl.get_rect().left + 50),
                                 int(window.get_height()*0.55)   ))

        pygame.draw.rect(window, plus_nbnpc_butt_color, plus_nbnpc_butt)
        pygame.draw.rect(window, minus_nbnpc_butt_color, minus_nbnpc_butt)

        plusnpc = font.render("+", True, basic_colors.BLACK)
        window.blit(plusnpc, (plus_nbnpc_butt.center[0] - (plusnpc.get_width()/2), 
                    plus_nbnpc_butt.center[1] - (plusnpc.get_height()/2) ) )

        minusnpc = font.render("-", True, basic_colors.BLACK)
        window.blit(minusnpc, (minus_nbnpc_butt.center[0] - (minusnpc.get_width()/2), 
                    minus_nbnpc_butt.center[1] - (minusnpc.get_height()/2) ) )

        pygame.draw.rect(window, plus_nbobs_butt_color, plus_nbobs_butt)
        pygame.draw.rect(window, minus_nbobs_butt_color, minus_nbobs_butt)

        window.blit(plusnpc, (plus_nbobs_butt.center[0] - (plusnpc.get_width()/2), 
                    plus_nbobs_butt.center[1] - (plusnpc.get_height()/2) ) )

        window.blit(minusnpc, (minus_nbobs_butt.center[0] - (minusnpc.get_width()/2), 
                    minus_nbobs_butt.center[1] - (minusnpc.get_height()/2) ) )

        fontsize = int(window.get_height()*0.2)
        font = pygame.font.SysFont('Sans', fontsize)
        text1 = font.render("Colony Life Simulator", True, basic_colors.WHITE)
        window.blit(text1, (window.get_rect().center[0] - (text1.get_width()/2),
                        window.get_height()*0.12 ) )

        pygame.display.flip()
    """

    #LOADING
    if run:
        env = Env.Environment(main_surface_width, main_surface_height)
        
        thread_loading = DisplayLoadingThread()

        thread_loading.start()

        for i in range(nb_obs):
            o = entities.Obstacle(random.randint(30, 100), random.randint(30, 100), env)
            o.setRandomPose(main_surface_width, main_surface_height)
            env.addObstacle(o)

        env.constructEnvironment(5)

        # pgo_obj = pgo.PositionnalGridOverlay(env, 20)

        # time.sleep(1)

        thread_loading.stop()
        thread_loading.join(2)



        DISPLAY_DEBUG = debug_displ
        DISPLAY_OVERLAY = False
        DISPLAY_RELATION = False
        DISPLAY_NAME = False
        DISPLAY_INTERACTION = False
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
            select_rect_surface = pygame.Surface((main_surface_width, main_surface_height), pygame.SRCALPHA)
            topleft_info = (topleft_screen[0]+main_surface_width, 0)
            info_surface = pygame.Surface((info_surface_width, info_surface_height), pygame.SRCALPHA)
        

        l_npc = []
        for i in range(nb_npc):
            entity = entities.NPC(env, name="npc"+str(i))
            entity.setRandomPose(main_surface_width, main_surface_height)
            entity.setIdleBehaviour()
            l_npc.append(entity)

        
        l_spawner = []
        for i in range(nb_spawner):
            spawnerFood = entities.Spawner(env, "spawner"+str(i), "foodspawner", 6, random.randint(620, 780), random.random()*0.4 + 0.8, False)
            spawnerFood.setRandomPose(main_surface_width, main_surface_height)
            spawnerFood.setSpawnerBehaviour()
            for i in range(1):
                spawnerFood.spawn(start_thread=False)
            l_spawner.append(spawnerFood)

        env.setNPCs(l_npc)
        env.setSpawners(l_spawner)

        NCT  = ct.NeighboursComputationThread(env)
        CFCT = ct.ClosestFoodComputationThread(env)

        for npc in env.npcs:
            npc.setNeigh_computation_thread(NCT)
            npc.setClosestfood_computation_thread(CFCT)
            env.pgo_obj.updatePosition(npc)
            npc.setInitialSocialXP()

        

        #Buttons
        offset_row1 = 10

        color_rect_button = basic_colors.BLUE
        color_rect_button_base = basic_colors.BLUE
        rect_button = pygame.Rect((main_surface_width + offset_row1, main_surface_height*0.94), (info_surface_width*0.25, info_surface_height*0.05))
        offset_row1 = offset_row1 + rect_button.width


        color_pause_button = basic_colors.OLIVE
        color_pause_button_base = basic_colors.OLIVE
        pause_button = pygame.Rect((main_surface_width + offset_row1 * 1.2, main_surface_height*0.94), 
                                    (info_surface_width*0.25, info_surface_height*0.05))
        offset_row1 = offset_row1 + pause_button.width
        
        color_quit_button = basic_colors.RED
        color_quit_button_base = basic_colors.RED
        quit_button = pygame.Rect((main_surface_width + offset_row1 * 1.2, main_surface_height*0.94), 
                                    (info_surface_width*0.25, info_surface_height*0.05))
        offset_row1 = offset_row1 + quit_button.width

        offset_row2 = 10

        color_info_button = basic_colors.YELLOW
        color_info_button_base = basic_colors.YELLOW
        info_button = pygame.Rect((main_surface_width + offset_row2, main_surface_height*0.87), 
                                    (info_surface_width*0.25, info_surface_height*0.05))
        
        offset_row2 = offset_row2 + info_button.width

        color_name_button = basic_colors.YELLOW
        color_name_button_base = basic_colors.YELLOW
        name_info_button = pygame.Rect((main_surface_width + offset_row2 * 1.2, main_surface_height*0.87), 
                                    (info_surface_width*0.25, info_surface_height*0.05))
        offset_row2 = offset_row2 + name_info_button.width

        offset_row3 = 10

        color_interact_button = basic_colors.YELLOW
        color_interact_button_base = basic_colors.YELLOW
        interact_button = pygame.Rect((main_surface_width + offset_row3, main_surface_height*0.80), 
                                    (info_surface_width*0.25, info_surface_height*0.05))
        offset_row3 = offset_row3 + interact_button.width

        color_relation_button = basic_colors.YELLOW
        color_relation_button_base = basic_colors.YELLOW
        relation_info_button = pygame.Rect((main_surface_width + offset_row3*1.2, main_surface_height*0.80), 
                                    (info_surface_width*0.25, info_surface_height*0.05))
        offset_row3 = offset_row3 + relation_info_button.width

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

        # print("wesh")

        #Start Threads
        NCT.start()
        CFCT.start()
        [x.start() for x in env.npcs]
        [x.start() for x in env.spawners]
        for kr in env.ressources.keys():
            for r in env.ressources[kr]:
                r.start()

        def handle_pause(paused):
            if paused:
                for e in env.npcs:
                    e.user_pause()
                for r in env.spawners:
                    r.user_pause()
                for kr in env.ressources.keys():
                    for r in env.ressources[kr]:
                        r.user_pause()
            else:
                for e in env.npcs:
                    e.user_resume()
                for r in env.spawners:
                    r.user_resume()
                for kr in env.ressources.keys():
                    for r in env.ressources[kr]:
                        r.user_resume()

        while run:

            t1 = time.time()
            if PROFIL:
                T_TOTAL = time.time()

                if curr_profiler%500 == 0:
                    pc.append_to("NB_NPC", len(env.npcs))
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
                select_rect_surface.fill(basic_colors.EMPTY)
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

            if name_info_button.collidepoint(mp):
                color_name_button = basic_colors.YELLOW_3
            elif DISPLAY_NAME:
                color_name_button = basic_colors.YELLOW_2
            else:
                color_name_button = basic_colors.YELLOW

            if relation_info_button.collidepoint(mp):
                color_relation_button = basic_colors.YELLOW_3
            elif DISPLAY_RELATION:
                color_relation_button = basic_colors.YELLOW_2
            else:
                color_relation_button = basic_colors.YELLOW

            if interact_button.collidepoint(mp):
                color_interact_button = basic_colors.YELLOW_3
            elif DISPLAY_INTERACTION:
                color_interact_button = basic_colors.YELLOW_2
            else:
                color_interact_button = basic_colors.YELLOW

            #Single event control
            if not PROFIL:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == K_ESCAPE :
                            run = False
                        elif event.key == K_SPACE:
                            paused = not paused
                            handle_pause(paused)
                        elif event.key == K_DELETE:
                            for n in selected_npc:
                                n.die()
                        elif event.key == K_d:
                            DISPLAY_DEBUG = not DISPLAY_DEBUG
                        elif event.key == K_i:
                            info = not info
                        elif event.key == K_o:
                            DISPLAY_OVERLAY = not DISPLAY_OVERLAY
                        elif event.key == K_n:
                            DISPLAY_NAME = not DISPLAY_NAME
                        elif event.key == K_t:
                            DISPLAY_INTERACTION = not DISPLAY_INTERACTION
                        elif event.key == pygame.K_a and pygame.key.get_mods() & pygame.KMOD_CTRL:
                            for e in env.npcs:
                                e.selected_npc = True
                            selected_npc = env.npcs
                            shift_list_ent_inf = 0
                            shift_list_ent_sup = shift_list_ent_span
                        elif event.key == pygame.K_r and pygame.key.get_mods() & pygame.KMOD_CTRL:
                            for e in env.npcs:
                                e.selected_npc = True
                            selected_npc = copy.copy(env.npcs)
                            np.random.shuffle(selected_npc)
                            selected_npc = selected_npc[:shift_list_ent_span]

                            shift_list_ent_inf = 0
                            shift_list_ent_sup = shift_list_ent_span
                        elif event.key == K_r:
                            DISPLAY_RELATION = not DISPLAY_RELATION
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
                            elif name_info_button.collidepoint(mp):
                                DISPLAY_NAME = not DISPLAY_NAME
                            elif relation_info_button.collidepoint(mp):
                                DISPLAY_RELATION = not DISPLAY_RELATION
                            elif interact_button.collidepoint(mp):
                                DISPLAY_INTERACTION = not DISPLAY_INTERACTION

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
                                        e.pause()
                                        e.setGOTOBehaviour(mp)
                                        e.resume()
                            # else:
                            #     spf = entities.Spawner(env, "spawner_user", "foodspawner", 10, 200, random.random()*0.6 + 0.8, False)
                            #     spf.setPose(mp[0], mp[1])
                            #     spf.setSpawnerBehaviour()
                            #     env.addSpawner(spf)
                            #     spf.start()
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
                                for e in env.npcs:
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

            #Logic
            t_update = time.time()
            if PROFIL:
                T_LOGIC = time.time()

            #Remove dead entities            
            for kr in env.ressources.keys():
                for deadres in [x for x in env.ressources[kr] if x.dead]:
                    deadres.join()
                env.ressources[kr] = [x for x in env.ressources[kr] if not x.dead]
            env.pgo_obj.updateRemoveDead()
            for deadnpc in [x for x in env.npcs if x.dead]:
                deadnpc.join()
            env.npcs = [x for x in env.npcs if not x.dead]

            if DISPLAY_RELATION:
                sprite.drawRelations(alpha_surface, env.npcs)

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

                if DISPLAY_OVERLAY:
                    for snpc in selected_npc:
                        # pygame.draw.rect(alpha_surface, basic_colors.ALPHA_WHITE, env.pgo_obj.positions[snpc], 1)

                        for r in snpc.neighbours_rect:
                            pygame.draw.rect(alpha_surface, basic_colors.ALPHA_WHITE, r, 1)
                        # pygame.draw.rect(alpha_surface, basic_colors.ALPHA_WHITE, snpc.neighbours_rect[0].unionall(snpc.neighbours_rect[1:]), 1)

                        # for r in env.pgo_obj.getRectInRangeLimit(snpc):
                        #     pygame.draw.rect(alpha_surface, basic_colors.ALPHA_RED, r, 1)

                #Display

                #Env
                for o in env.obstacles:
                    o.sprite.draw(screen)
                for i in range(1, len(env.river_path)):
                    pygame.draw.line(screen, basic_colors.BLUE, env.river_path[i-1], env.river_path[i], 5)
                for r in env.saved_rect_from_river:
                    pygame.draw.rect(screen, basic_colors.BLUE, r)
                    
                #Entities
                for sp in env.spawners:
                    sp.pause()
                    sp.sprite.draw(screen, info)
                    sp.resume()
                for kr in env.ressources.keys():
                    for r in env.ressources[kr]:
                        r.pause()
                        r.sprite.draw(screen, alpha_surface, info)
                        r.resume()
                for e in env.npcs:
                    e.pause()
                    e.sprite.draw(screen, DISPLAY_NAME)
                    if e in selected_npc:
                        e.sprite.drawSelected(screen, alpha_surface, basic_colors.RED)
                    if e.dead:
                        e.sprite.drawDead(screen)
                    e.resume()
                
                pc.draw_relation_sprites(screen, paused, DISPLAY_INTERACTION)
                
                if selection_rect != None and hasattr(selection_rect, "rect"):
                    # print selection_rect.rect
                    selection_rect.draw(select_rect_surface)

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
                text3 = "Selected Entities ({0}/{1}) :".format(str(len(selected_npc)), str(len(env.npcs)))
                displ_text = font.render(text, True, basic_colors.BLACK)
                displ_text2 = font.render(text2, True, basic_colors.BLACK)
                displ_text3 = font.render(text3, True, basic_colors.BLACK)
                info_surface.blit(displ_text, (10, fontsize*1.2))
                shift = fontsize*1.2
                info_surface.blit(displ_text2, (10, fontsize*1.2 + shift))
                shift = fontsize*1.2 + shift
                info_surface.blit(displ_text3, (10, fontsize*2 + shift))
                shift = fontsize*2 + shift


                # print (shift_list_ent_inf, shift_list_ent_sup)
                if shift_list_ent_inf > 0:
                    txt_dotdotdot = "..."
                    displ_dotdotdot = font.render(txt_dotdotdot, True, basic_colors.BLACK)
                    info_surface.blit(displ_dotdotdot, (10, shift + fontsize + 2))
                    shift = shift + fontsize + 2

                for e in selected_npc[shift_list_ent_inf:shift_list_ent_sup]:
                    txt_basic     = "{} | {}/{} HP (regen {}%) | {}/{} XP".format(e.name, e.hitpoint, e.hitpoint_max, round(e.regen_hitpoint*100, 2), e.global_xp, e.global_xp_next_lvl)
                    txt_basic2    = "{} years old | level {} | Gen {} | Parents : {} & {}".format(e.age, e.level, e.generation, e.parents[0].name if e.parents[0] != None else "None", e.parents[1].name if e.parents[1] != None else "None")
                    txt_stat1     = "  - speed : {}  memory : {}".format(str(e.speed), str(e.memory))
                    txt_hunger    = "  - hunger : {}/{} - Kin : {} Cou : {} Str : {}".format(e.hunger, e.hunger_max, e.kindness, e.courage, e.strength)
                    txt_stat2     = "  - Atck : +{} ({}d{}+{}) | Def : {}".format(e.attack, e.attack_dice[0], e.attack_dice[1], e.attack_damage, e.defense)
                    txt_behaviour = "  - state : {}".format((e.behaviour.label if e.behaviour != None else "none"))
                    txt_social    = "  - Last soc. int. : {}".format(e.last_social_interaction)
                    
                    displ_txt_basic = font.render(txt_basic, True, basic_colors.BLACK)
                    displ_txt_basic2 = font.render(txt_basic2, True, basic_colors.BLACK)
                    displ_txt_stat1 = font.render(txt_stat1, True, basic_colors.BLACK)
                    displ_txt_hunger = font.render(txt_hunger, True, basic_colors.BLACK)
                    displ_txt_stat2 = font.render(txt_stat2, True, basic_colors.BLACK)
                    displ_txt_behaviour = font.render(txt_behaviour, True, basic_colors.BLACK)
                    displ_txt_social = font.render(txt_social, True, basic_colors.BLACK)

                    info_surface.blit(displ_txt_basic, (10, shift + fontsize + 2))
                    shift = shift + fontsize + 2
                    info_surface.blit(displ_txt_basic2, (10, shift + fontsize + 2))
                    shift = shift + fontsize
                    info_surface.blit(displ_txt_stat1, (10, shift + fontsize))
                    shift = shift + fontsize
                    info_surface.blit(displ_txt_hunger, (10, shift + fontsize))
                    shift = shift + fontsize
                    info_surface.blit(displ_txt_stat2, (10, shift + fontsize))
                    shift = shift + fontsize
                    info_surface.blit(displ_txt_behaviour, (10, shift + fontsize))
                    shift = shift + fontsize
                    info_surface.blit(displ_txt_social, (10, shift + fontsize))
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

                quit_text   = font.render("Quit (ESC)", True, basic_colors.BLACK)

                rect_text   = font.render("Rect (D)", True, basic_colors.BLACK)

                paused_text = font.render("Pause (SPC)", True, basic_colors.BLACK)

                info_text = font.render("Info (I)", True, basic_colors.BLACK)
                
                name_info_text = font.render("Name (N)", True, basic_colors.BLACK)
                
                relation_info_text = font.render("Relation (R)", True, basic_colors.BLACK)

                interact_text = font.render("Interact. (T)", True, basic_colors.BLACK)

                #Blit and Flip surfaces
                window.blit(screen, (0, 0))
                window.blit(alpha_surface, (0, 0))
                window.blit(select_rect_surface, (0, 0))
                window.blit(info_surface, (main_surface_width, 0))

                # pygame.draw.rect(window, color_quit_button, quit_button)
                draw_button(window, color_quit_button, color_quit_button_base, quit_button, border=4)
                window.blit(quit_text, (quit_button.center[0] - (quit_text.get_width()/2), 
                    quit_button.center[1] - (quit_text.get_height()/2) ) )

                # pygame.draw.rect(window, color_rect_button, rect_button)
                draw_button(window, color_rect_button, color_rect_button_base, rect_button, border=4)
                window.blit(rect_text, (rect_button.center[0] - (rect_text.get_width()/2), 
                    rect_button.center[1] - (rect_text.get_height()/2) ))

                # pygame.draw.rect(window, color_pause_button, pause_button)
                draw_button(window, color_pause_button, color_pause_button_base, pause_button, border=4)
                window.blit(paused_text, (pause_button.center[0] - (paused_text.get_width()/2), 
                    pause_button.center[1] - (paused_text.get_height()/2) ) )

                # pygame.draw.rect(window, color_info_button, info_button)
                draw_button(window, color_info_button, color_info_button_base, info_button, border=4)
                window.blit(info_text, (info_button.center[0] - (info_text.get_width()/2), 
                    info_button.center[1] - (info_text.get_height()/2) ) )

                # pygame.draw.rect(window, color_name_button, name_info_button)
                draw_button(window, color_name_button, color_name_button_base, name_info_button, border=4)
                window.blit(name_info_text, (name_info_button.center[0] - (name_info_text.get_width()/2), 
                    name_info_button.center[1] - (name_info_text.get_height()/2) ) )

                # pygame.draw.rect(window, color_relation_button, relation_info_button)
                draw_button(window, color_relation_button, color_relation_button_base, relation_info_button, border=4)
                window.blit(relation_info_text, (relation_info_button.center[0] - (relation_info_text.get_width()/2), 
                    relation_info_button.center[1] - (relation_info_text.get_height()/2) ) )

                draw_button(window, color_interact_button, color_interact_button_base, interact_button, border=4)
                window.blit(interact_text, (interact_button.center[0] - (interact_text.get_width()/2), 
                    interact_button.center[1] - (interact_text.get_height()/2) ) )

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

        for e in env.npcs:
            e.die()
            e.update()
            # e.join(2)

        for sp in env.spawners:
            sp.die()
            sp.update()
            # sp.join(2)

        for kr in env.ressources.keys():
            for r in env.ressources[kr]:
                r.die()
                r.update()
                # r.join(2)
        
        NCT.stop()
        CFCT.stop()

        quittin_screen_thread = QuitScreenThead()

        quittin_screen_thread.start()    

        th_list_kill = []
        th_list_kill.extend(env.npcs)
        th_list_kill.extend(env.spawners)
        for kr in env.ressources.keys():
            th_list_kill.extend(env.ressources[kr])
        th_list_kill.append(NCT)
        th_list_kill.append(CFCT)

        pc.set("TOTAL_QUITTING_THREAD", len(th_list_kill))

        i = 0
        for t in th_list_kill:
            i += 1
            pc.set("CURRENT_QUIT_THREAD_NAME", t.name)
            t.join(2)
            pc.set("CURRENT_QUITTING_THREAD", i)
            time.sleep(0.01)

        quittin_screen_thread.stop()
        quittin_screen_thread.join()    

        # NCT.stop()
        # NCT.join(2)

        # CFCT.stop()
        # CFCT.join(2)

        print("End !")


if __name__ == '__main__':
    main(_profiler=-1, DISPLAY=True, debug_displ=False)
    # init = InitialisationScreen()
    # init.start()

    # while init.is_running:
    #     pass

    # init.stop()
    # init.join(2)