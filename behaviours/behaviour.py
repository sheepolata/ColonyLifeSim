import random

import utils.utils as utils
import utils.geometry as geo
import utils.pathfinding as pf

class Behaviour(object):
    def __init__(self, entity, env):
        super(Behaviour, self).__init__()
        
        self.entity = entity
        self.env = env

        self.state = "Nothing"
        self.label = "NaN"

    def computePath(self):
        pass

    def nextStep(self):
        pass

    def getPath(self):
        return self.path[self.ipath]

class IdleBehaviour(Behaviour):
    def __init__(self, entity, env):
        super(IdleBehaviour, self).__init__(entity, env)
        
        self.path = []
        self.ipath = 0

        self.state = "Idle"
        self.label = "I"

        self.collision_debug = []

    def computePath(self):
        del self.path[:]
        self.path.append(self.entity.getPose())

        rdspan = 75

        target = (0, 0)

        tx = self.entity.getPose()[0] + random.randint(-rdspan, rdspan)
        ty = self.entity.getPose()[1] + random.randint(-rdspan, rdspan)
        while self.env.collideOneObstacle_Point((tx, ty)):
            tx = self.entity.getPose()[0] + random.randint(-rdspan, rdspan)
            ty = self.entity.getPose()[1] + random.randint(-rdspan, rdspan)

        target = (tx, ty)

        current_rect = self.env.getCurrentRect(self.entity.getPose())
        if current_rect == None:
            print("Error, no current rect found")
            return

        target_rect = self.env.getCurrentRect(target)
        if target_rect == None:
            print("Error, no target rect found")
            return

        path_astar = pf.astar(current_rect.center, target_rect.center , self.env)

        if path_astar == None:
            print("Error, no path found")
            return

        self.path.append(self.entity.getPose())
        for p in reversed(path_astar):
            self.path.append(p)
        self.path.append(target)



    def nextStep(self):

        if not self.path or self.ipath >= len(self.path):
            return

        target = self.path[self.ipath]


        if utils.near(self.entity.getPose(), target, _thresh=self.entity.speed + 1):
            self.ipath += 1
            self.entity.shift_x = 0
            self.entity.shift_y = 0
            if self.ipath >= len(self.path):
                self.computePath()
                self.ipath = 0
            return


        if self.entity.pose.x > target[0]:
            self.entity.shift_x = -self.entity.speed
        if self.entity.pose.x < target[0]:
            self.entity.shift_x = self.entity.speed
        if self.entity.pose.x == target[0]:
            self.entity.shift_x = 0

        if self.entity.pose.y > target[1]:
            self.entity.shift_y = -self.entity.speed
        if self.entity.pose.y < target[1]:
            self.entity.shift_y = self.entity.speed
        if self.entity.pose.y == target[1]:
            self.entity.shift_y = 0



        




