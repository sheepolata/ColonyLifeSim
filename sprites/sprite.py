import pygame
import utils.basic_colors as basic_colors


class SpriteEntityBase(object):
    """docstring for SpriteEntityBase"""
    def __init__(self, color, pose):
        self.color = color
        self.pose = pose

        self.size = 10
        
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
        if line and self.npc.behaviour != None:
            for p in range(1, len(self.npc.behaviour.path)):
                dep = self.npc.behaviour.path[p-1]
                # dep = self.npc.getPose()
                arr = self.npc.behaviour.path[p]
                # arr = self.npc.behaviour.target
                pygame.draw.line(line_surface, basic_colors.ALPHA_WHITE, dep, arr)


        