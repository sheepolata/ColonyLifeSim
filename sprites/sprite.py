import pygame
import utils.basic_colors as basic_colors
from pygame.locals import *

import copy
import utils.utils as utils


class SpriteEntityBase(object):
    """docstring for SpriteEntityBase"""
    def __init__(self, color, pose):
        self.color = color
        self.pose = pose

        self.size = 4
        
        self.rect = pygame.Rect(pose.x-(self.size/2), pose.y-(self.size/2), self.size, self.size)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.rect.center, self.size)

    def update(self, pose): 
        self.pose = pose
        self.rect = pygame.Rect(pose.x-(self.size/2), pose.y-(self.size/2), self.size, self.size)


class SpriteObstacle(SpriteEntityBase):
    def __init__(self, color, pose, sizew, sizeh):
        super(SpriteObstacle, self).__init__(color, pose)

        self.sizew = sizew
        self.sizeh = sizeh

        self.rect = pygame.Rect(self.pose.x-(self.sizew/2), self.pose.y-(self.sizeh/2), self.sizew, self.sizeh)

    def draw(self, screen):
        self.rect = pygame.Rect(self.pose.x-(self.sizew/2), self.pose.y-(self.sizeh/2), self.sizew, self.sizeh)
        # print self.rect

        pygame.draw.rect(screen, self.color, self.rect)

def drawRelations(line_surface, list_npcs):
    for npc in list_npcs:
        for n in npc.neighbours:
            if npc.social_xp[n] > -25 and npc.social_xp[n] < 0:
                pygame.draw.line(line_surface, basic_colors.ALPHA_WHITE, npc.sprite.rect.center, n.sprite.rect.center, int(utils.normalise(npc.social_xp[n], -25, 0)*5 + 1))
            elif npc.social_xp[n] >= 0 and npc.social_xp[n] < 25:
                pygame.draw.line(line_surface, basic_colors.ALPHA_WHITE, npc.sprite.rect.center, n.sprite.rect.center, int(utils.normalise(npc.social_xp[n], 0, 25)*5 + 1))
            elif npc.social_xp[n] > 25:
                c = (0, min(100*utils.normalise(npc.social_xp[n], 25, 100)+155, 255), 0, 128)
                pygame.draw.line(line_surface, c, npc.sprite.rect.center, n.sprite.rect.center, int(utils.normalise(npc.social_xp[n], 25, 100)*5 + 1))
            elif npc.social_xp[n] < -25:
                c = (min(100*utils.normalise(npc.social_xp[n], -25, -100)+155, 255), 0, 0, 128)
                pygame.draw.line(line_surface, c, npc.sprite.rect.center, n.sprite.rect.center, int(utils.normalise(npc.social_xp[n], -25, -100)*5 + 1))

class SpriteNPC(SpriteEntityBase):
    def __init__(self, color, pose, npc):
        super(SpriteNPC, self).__init__(color, pose)
        self.npc = npc

    def draw(self, screen, info):
        super(SpriteNPC, self).draw(screen)


        if info:
            text = self.npc.name
            font = pygame.font.SysFont('Sans', 10)
            displ_text = font.render(text, True, basic_colors.BLACK)
            screen.blit(displ_text, (self.rect.center[0]-self.size*3, int(self.rect.center[1]-self.size*2.5)))

    def drawDead(self, screen):
        pygame.draw.line(screen, basic_colors.ALPHA_RED, self.rect.topleft, self.rect.bottomright, 2)
        pygame.draw.line(screen, basic_colors.ALPHA_RED, self.rect.topright, self.rect.bottomleft, 2)


    def drawSelected(self, screen, line_surface, color):
        pygame.draw.circle(screen, color, self.rect.center, self.size, 1)
        
        pygame.draw.circle(line_surface, basic_colors.ALPHA_RED_2, self.rect.center, self.npc.vision_radius, 1)

        text = self.npc.name
        font = pygame.font.SysFont('Sans', 10)
        displ_text = font.render(text, True, basic_colors.BLACK)
        screen.blit(displ_text, (self.rect.center[0]-self.size*3, int(self.rect.center[1]-self.size*2.5)))

        for n in self.npc.neighbours:
            if self.npc.social_xp[n] > -25 and self.npc.social_xp[n] < 0:
                pygame.draw.line(line_surface, basic_colors.ALPHA_WHITE, self.rect.center, n.sprite.rect.center, int(utils.normalise(self.npc.social_xp[n], -25, 0)*5 + 1))
            elif self.npc.social_xp[n] >= 0 and self.npc.social_xp[n] < 25:
                pygame.draw.line(line_surface, basic_colors.ALPHA_WHITE, self.rect.center, n.sprite.rect.center, int(utils.normalise(self.npc.social_xp[n], 0, 25)*5 + 1))
            elif self.npc.social_xp[n] > 25:
                c = (0, 100*utils.normalise(self.npc.social_xp[n], 25, 100)+155, 0, 128)
                pygame.draw.line(line_surface, c, self.rect.center, n.sprite.rect.center, int(utils.normalise(self.npc.social_xp[n], 25, 100)*5 + 1))
            elif self.npc.social_xp[n] < -25:
                c = (100*utils.normalise(self.npc.social_xp[n], -25, -100)+155, 0, 0, 128)
                pygame.draw.line(line_surface, c, self.rect.center, n.sprite.rect.center, int(utils.normalise(self.npc.social_xp[n], -25, -100)*5 + 1))
        for vr in self.npc.known_food.keys():
            pygame.draw.line(line_surface, basic_colors.ALPHA_WHITE, self.rect.center, vr.sprite.rect.center)

        if self.npc.behaviour != None:
            current_path = copy.copy(self.npc.behaviour.path)
            if len(current_path) >= 2:
                for p in range(1, len(current_path)):
                    dep = current_path[p-1]
                    # dep = self.npc.getPose()
                    arr = current_path[p]
                    # arr = self.npc.behaviour.target
                    pygame.draw.line(line_surface, basic_colors.ALPHA_WHITE_2, dep, arr)



class SpriteRessource(SpriteEntityBase):
    """docstring for SpriteRessource"""
    def __init__(self, ressource, pose):
        self.ressource = ressource

        color = basic_colors.WHITE
        if self.ressource.name == "food":
            color = basic_colors.LIME

        self.color_non_havestable = basic_colors.ALPHA_RED

        super(SpriteRessource, self).__init__(color, pose)

        self.size = 4

    def draw(self, screen, alpha_surface, info):
        # super(SpriteRessource, self).draw(screen)
        s = int((self.ressource.value / self.ressource.max_value)*self.size + 2) if self.ressource.max_value != 0 else self.size
        pygame.draw.circle(screen, self.color, self.rect.center, s)


        if not self.ressource.harvestable:
            pygame.draw.circle(alpha_surface, self.color_non_havestable, self.rect.center, self.size)

        if info:
            text = str(self.ressource.value)
            font = pygame.font.SysFont('Sans', 10)
            displ_text = font.render(text, True, basic_colors.BLACK)
            screen.blit(displ_text, self.rect.center)

            pygame.draw.line(alpha_surface, basic_colors.ALPHA_WHITE, self.rect.center, self.ressource.spawner.sprite.rect.center)

class SpriteSpawner(SpriteEntityBase):
    """docstring for SpriteRessource"""
    def __init__(self, spawner, pose):
        self.spawner = spawner

        color = basic_colors.WHITE

        self.color_non_havestable = basic_colors.ALPHA_RED

        super(SpriteSpawner, self).__init__(color, pose)

    def draw(self, screen, info):
        if info:
            super(SpriteSpawner, self).draw(screen)

            # text = str(self.spawner.name)
            # font = pygame.font.SysFont('Sans', 10)
            # displ_text = font.render(text, True, basic_colors.BLACK)
            # screen.blit(displ_text, (self.rect.center[0]-self.size, self.rect.center[1]-self.size))


        