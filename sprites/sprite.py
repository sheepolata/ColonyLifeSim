import pygame
import utils.basic_colors as basic_colors
from pygame.locals import *


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

    def draw(self, screen, line_surface, line=False):
        super(SpriteNPC, self).draw(screen)

        text = str(self.npc.hunger)
        font = pygame.font.SysFont('Sans', 10)
        displ_text = font.render(text, True, basic_colors.BLACK)
        screen.blit(displ_text, (self.rect.center[0]-self.size*3, int(self.rect.center[1]-self.size*2.5)))


        if line and self.npc.behaviour != None:
            for p in range(1, len(self.npc.behaviour.path)):
                dep = self.npc.behaviour.path[p-1]
                # dep = self.npc.getPose()
                arr = self.npc.behaviour.path[p]
                # arr = self.npc.behaviour.target
                pygame.draw.line(line_surface, basic_colors.ALPHA_WHITE, dep, arr)


class SpriteRessource(SpriteEntityBase):
    """docstring for SpriteRessource"""
    def __init__(self, ressource, pose):
        self.ressource = ressource

        color = basic_colors.WHITE
        if self.ressource.name == "food":
            color = basic_colors.LIME

        self.color_non_havestable = basic_colors.ALPHA_RED

        super(SpriteRessource, self).__init__(color, pose)

    def draw(self, screen, alpha_surface):
        super(SpriteRessource, self).draw(screen)
        if not self.ressource.harvestable:
            pygame.draw.circle(alpha_surface, self.color_non_havestable, self.rect.center, self.size)

        text = str(self.ressource.value)
        font = pygame.font.SysFont('Sans', 10)
        displ_text = font.render(text, True, basic_colors.BLACK)
        screen.blit(displ_text, self.rect.center)

class SpriteSpawner(SpriteEntityBase):
    """docstring for SpriteRessource"""
    def __init__(self, spawner, pose):
        self.spawner = spawner

        color = basic_colors.WHITE
        if self.spawner.name == "foodspawner":
            color = basic_colors.LIME

        self.color_non_havestable = basic_colors.ALPHA_RED

        super(SpriteSpawner, self).__init__(color, pose)

    def draw(self, screen):
        super(SpriteSpawner, self).draw(screen)

        text = str(self.spawner.name)
        font = pygame.font.SysFont('Sans', 10)
        displ_text = font.render(text, True, basic_colors.BLACK)
        screen.blit(displ_text, (self.rect.center[0]-self.size, self.rect.center[1]-self.size))


        