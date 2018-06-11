
import entities.entity as entities
import environment.environment as Env
import behaviours.behaviour as behaviour

import utils.pathfinding as pf
import utils.utils as utils
import utils.basic_colors as basic_colors

import pygame
import random
import sys


from screeninfo import get_monitors
monitor = get_monitors()[0]

# width, height = 860, 680
width, height = int(monitor.width*0.75), int(monitor.height*0.75)

import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % ((monitor.width/2)-(width/2),(monitor.height/2)-(height/2))


from pygame.locals import *

pygame.init()

#Generate zip file for ready-to-use windows app (in root directory) : C:/Python27/Scripts/pyinstaller main.py

def main():
    DISPLAY_DEBUG = False

    env = Env.Environment(width, height)

    clock = pygame.time.Clock()

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Colony Life Sim")
    alpha_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    
    for i in range(10):
        o = entities.Obstacle(random.randint(30, 100), random.randint(30, 100), env)
        o.setRandomPose(width, height)
        env.addObstacle(o)
    env.splitEnvironment()
    env.constructGraph(Env.areNeigbhoursSquare)
    env.constructRiver(5)


    l_entities = []
    for i in range(10):
        entity = entities.NPC(env, "entity"+str(i))
        entity.setRandomPose(width, height)
        entity.setIdleBehaviour()
        l_entities.append(entity)

    l_spawner = []
    for i in range(2):
        spawnerFood = entities.Spawner(env, "spawner"+str(i), "foodspawner", random.randint(560, 640), random.random()*0.6 + 0.8)
        spawnerFood.setRandomPose(width, height)
        spawnerFood.setSpawnerBehaviour()
        for i in range(3):
            spawnerFood.spawn()
        l_spawner.append(spawnerFood)


    run = True
    while run:
        clock.tick(60) #tick at 60fps

        screen.fill(basic_colors.GREEN)
        alpha_surface.fill(basic_colors.EMPTY)

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
                    mp = pygame.mouse.get_pos()
                    rect = env.getCurrentRect(mp)
                    if rect != None:
                        for e in l_entities:
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
                #MMB
                if event.button == 2:
                    pass
                #RMB
                if event.button == 3:
                    mp = pygame.mouse.get_pos()
                    rect = env.collideOneObstacle_Point(mp)
                    if rect != None:
                        res = entities.Ressource(env, "food", random.randint(30, 70), False)
                        res.setPose(mp[0], mp[1])
                        res.setRegrowBehaviour()
                        env.addRessource(res)
                    pass
                #Mouth Wheel up
                if event.button == 4:
                    pass
                #Mouth Wheel down
                if event.button == 5:
                    pass

        #Logic
        #play each entity
        for e in l_entities:
            e.update()
        for r in l_spawner:
            r.update()
        for kr in env.ressources.keys():
            for r in env.ressources[kr]:
                r.update()
            env.ressources[kr] = [x for x in env.ressources[kr] if not x.dead]
                

        #Remove dead entities
        l_entities = [x for x in l_entities if not x.dead]

        #Display Debug
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
        for e in l_entities:
            e.sprite.draw(screen, alpha_surface, True)
        for sp in l_spawner:
            sp.sprite.draw(screen)
        


        screen.blit(alpha_surface, (0, 0))
        pygame.display.flip()

    for e in l_entities:
        e.die()
        e.update()

    for kr in env.ressources.keys():
        for r in env.ressources[kr]:
            r.die()
            r.update()

    print("End !")


if __name__ == '__main__':
    main()