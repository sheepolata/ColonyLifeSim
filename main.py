
import entities.entity as entities
import environment.environment as Env
import behaviours.behaviour as behaviour

import utils.utils as utils
import utils.basic_colors as basic_colors

import pygame
import random
import sys

width, height = 860, 680

from screeninfo import get_monitors
monitor = get_monitors()[0]

import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % ((monitor.width/2)-(width/2),(monitor.height/2)-(height/2))

from pygame.locals import *

pygame.init()

def main():
    env = Env.Environment(width, height)

    def display_loading(env, screen):
        text = "Loading... " + str(env.loading) + "%"
        font = pygame.font.SysFont('Sans', int(50))
        display_text = font.render(text, True, (255, 255, 255))
        screen.blit(display_text, (env.width / 2, env.height / 2))

    for i in range(30):
        o = entities.Obstacle(random.randint(30, 100), random.randint(30, 100), env)
        o.setRandomPose(width, height)
        env.addObstacle(o)


    clock = pygame.time.Clock()

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Colony Life Sim")
    alpha_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    
    env.splitEnvironment()
    env.constructGraph()

    l_entities = []
    for i in range(10):
        entity = entities.NPC(env)
        # entity.setPose(50, 50)
        entity.setRandomPose(width, height)
        entity.setBaseBehaviour()
        l_entities.append(entity)


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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                #LMB
                if event.button == 1:
                    mp = pygame.mouse.get_pos()
                    rect = env.collideOneObstacle_Point(mp)
                    if rect != None:
                        for e in l_entities:
                            if isinstance(e.behaviour, behaviour.GOTOBehaviour):
                                e.behaviour.setSpecificTarget(mp)
                            else:
                                e.setGOTOBehaviour(mp)
                    pass
                #MMB
                if event.button == 2:
                    pass
                #RMB
                if event.button == 3:
                    pass
                #Mouth Wheel up
                if event.button == 4:
                    pass
                #Mouth Wheel down
                if event.button == 5:
                    pass

        #Logic
        
        #Display
        #Env
        for o in env.obstacles:
            o.sprite.draw(screen)

        for k in env.graph.keys():
            for pos in env.graph[k]:
                # print env.graph[k][pos]/10
                pygame.draw.line(screen, basic_colors.RED, k, pos, 1)

        #Entities
        for e in l_entities:
            e.update()
            e.sprite.draw(screen, alpha_surface, True)
            # e.drawDebugCollision(alpha_surface)

        for r in env.graph_rect:
            pygame.draw.rect(alpha_surface, basic_colors.ALPHA_WHITE, r, 1)




        screen.blit(alpha_surface, (0, 0))
        pygame.display.flip()

    print("End !")


if __name__ == '__main__':
    main()