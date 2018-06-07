import utils.utils as utils
import utils.basic_colors as basic_colors
import behaviours.behaviour as behaviour
import random
import sprites.sprite 

import pygame

class Entity(object):
    def __init__(self, env):
        self.pose = utils.Pose(0, 0)
        self.env = env

        self.sprite = sprites.sprite.SpriteEntityBase(basic_colors.CYAN, self.pose)

    def setPose(self, x, y):
        self.pose.x = x
        self.pose.y =y

    def getPose(self):
        return self.pose.getPose()

    def setRandomPose(self, maxx, maxy):
        self.pose.setPose(random.randint(0, maxx), random.randint(0, maxy))

    def update(self):
        # self.pose.setPose(x, y)
        self.sprite.update(self.pose)

    def drawDebugCollision(self, surface):
        pass

class NPC(Entity):
    def __init__(self, env):
        super(NPC, self).__init__(env)

        self.shift_x = 0
        self.shift_y = 0
        self.speed = 1

        self.sprite = sprites.sprite.SpriteNPC(basic_colors.CYAN, self.pose, self)

    def setBaseBehaviour(self):
        self.behaviour = behaviour.IdleBehaviour(self, self.env)
        self.behaviour.computePath()

    def setRandomPose(self, maxx, maxy):
        super(NPC, self).setRandomPose(maxx, maxy)
        while self.env.collideOneObstacle_Point(self.getPose()) or self.env.getCurrentRect(self.getPose()) == None:
            super(NPC, self).setRandomPose(maxx, maxy)
            

    def drawDebugCollision(self, surface):
        super(NPC, self).drawDebugCollision(surface)
        for c in filter(lambda a: a != None, self.behaviour.collision_debug):
            pygame.draw.circle(surface, basic_colors.ALPHA_RED, c, 3)

    def update(self):
        super(NPC, self).update()

        self.behaviour.nextStep()


        self.pose.x += self.shift_x
        self.pose.y += self.shift_y

        # self.pose.x += self.speed * utils.getSign(self.shift_x)
        # self.shift_x += 1 * utils.getSign(self.shift_x)

        # self.pose.y += self.speed * utils.getSign(self.shift_y)
        # self.shift_y += 1 * utils.getSign(self.shift_y)
        

class Obstacle(Entity):
    def __init__(self, sizew, sizeh, env):
        super(Obstacle, self).__init__(env)
        
        self.sizew = sizew

        self.sizeh = sizeh

        self.sprite = sprites.sprite.SpriteObstacle(basic_colors.MAROON, self.pose, self.sizew, self.sizeh)
        
    def setRandomPose(self, maxx, maxy):
        super(Obstacle, self).setRandomPose(maxx, maxy)
        self.sprite.rect = pygame.Rect(self.sprite.pose.x-(self.sprite.sizew/2), self.sprite.pose.y-(self.sprite.sizeh/2), self.sprite.sizew, self.sprite.sizeh)
