import pygame
import utils.basic_colors as basic_colors
from pygame.locals import *

import copy


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

    def drawSelected(self, screen, line_surface, color):
        pygame.draw.circle(screen, color, self.rect.center, self.size, 1)
        
        pygame.draw.circle(line_surface, basic_colors.ALPHA_RED_2, self.rect.center, self.npc.vision_radius, 1)
        # r = pygame.draw.circle(line_surface, basic_colors.ALPHA_RED_2, self.rect.center, entity.vision_radius, 1)
        # pygame.draw.rect(line_surface, basic_colors.ALPHA_RED_2, r, 1)

        # for r in self.npc.env.pgo_obj.getRectInRangeStrict(self.npc):
        #     pygame.draw.rect(line_surface, basic_colors.ALPHA_WHITE, r, 1)

        text = self.npc.name
        font = pygame.font.SysFont('Sans', 10)
        displ_text = font.render(text, True, basic_colors.BLACK)
        screen.blit(displ_text, (self.rect.center[0]-self.size*3, int(self.rect.center[1]-self.size*2.5)))

        for n in self.npc.neighbours:
            if self.npc.isFriend(n):
                pygame.draw.line(line_surface, basic_colors.ALPHA_LIME, self.rect.center, n.sprite.rect.center)
            else:
                pygame.draw.line(line_surface, basic_colors.ALPHA_RED, self.rect.center, n.sprite.rect.center)
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

    def draw(self, screen, alpha_surface, info):
        super(SpriteRessource, self).draw(screen)
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


        