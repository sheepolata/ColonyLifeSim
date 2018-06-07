import random

import utils.utils as utils
import utils.geometry as geo
import utils.pathfinding as pf

class Behaviour(object):
    def __init__(self, entity, env):
        super(Behaviour, self).__init__()
        
        self.entity = entity
        self.env = env

        self.path = []
        self.ipath = 0

        self.state = "Nothing"
        self.label = "NaN"

        self.target = self.entity.getPose()

    def computePath(self, _target):

        current_rect = self.env.getCurrentRect(self.entity.getPose())
        if current_rect == None:
            # print("Error, no current rect found")
            self.entity.setPose(self.entity.getPose()[0] + random.randint(-4, 4), self.entity.getPose()[1]+ random.randint(-4, 4))
            return

        target_rect = self.env.getCurrentRect(_target)
        trial = 0
        if target_rect == None:
            # print("Error, no self.target rect found")
            return

        self.target = _target

        self.path.append(self.entity.getPose())

        # if self.env.lineCollideObstacle(self.entity.getPose(), self.target):
        path_astar = pf.astar(current_rect.center, target_rect.center , self.env)

        if path_astar == None:
            print("Error, no path found")
            return
        for p in reversed(path_astar):
            self.path.append(p)

        self.path.append(self.target)

    def nextStep(self):
        if not self.path or self.ipath >= len(self.path):
            return -1

        self.target = self.path[self.ipath]


        if utils.near(self.entity.getPose(), self.target, _thresh=self.entity.speed + 1):
            self.ipath += 1
            self.entity.shift_x = 0
            self.entity.shift_y = 0
            if self.ipath >= len(self.path):
                self.ipath = 0
                del self.path[:]
            return 0


        if self.entity.pose.x > self.target[0]:
            self.entity.shift_x = -self.entity.speed
        if self.entity.pose.x < self.target[0]:
            self.entity.shift_x = self.entity.speed
        if self.entity.pose.x == self.target[0]:
            self.entity.shift_x = 0

        if self.entity.pose.y > self.target[1]:
            self.entity.shift_y = -self.entity.speed
        if self.entity.pose.y < self.target[1]:
            self.entity.shift_y = self.entity.speed
        if self.entity.pose.y == self.target[1]:
            self.entity.shift_y = 0

        return 1

    def getPath(self):
        return self.path[self.ipath]

class IdleBehaviour(Behaviour):
    def __init__(self, entity, env):
        super(IdleBehaviour, self).__init__(entity, env)

        self.state = "Idle"
        self.label = "I"

        self.collision_debug = []

    def computePath(self):
        del self.path[:]
        self.path.append(self.entity.getPose())

        rdspan = 75

        tx = self.entity.getPose()[0] + random.randint(-rdspan, rdspan)
        ty = self.entity.getPose()[1] + random.randint(-rdspan, rdspan)
        while self.env.collideOneObstacle_Point((tx, ty)):
            tx = self.entity.getPose()[0] + random.randint(-rdspan, rdspan)
            ty = self.entity.getPose()[1] + random.randint(-rdspan, rdspan)

        _target = (tx, ty)

        super(IdleBehaviour, self).computePath(_target)

    def nextStep(self):
        if not self.path or self.ipath >= len(self.path):
            return -1 

        self.target = self.path[self.ipath]


        if utils.near(self.entity.getPose(), self.target, _thresh=self.entity.speed + 1):
            self.ipath += 1
            self.entity.shift_x = 0
            self.entity.shift_y = 0
            if self.ipath >= len(self.path):
                self.computePath()
                self.ipath = 0
            return 0

        if self.entity.pose.x > self.target[0]:
            self.entity.shift_x = -self.entity.speed
        if self.entity.pose.x < self.target[0]:
            self.entity.shift_x = self.entity.speed
        if self.entity.pose.x == self.target[0]:
            self.entity.shift_x = 0

        if self.entity.pose.y > self.target[1]:
            self.entity.shift_y = -self.entity.speed
        if self.entity.pose.y < self.target[1]:
            self.entity.shift_y = self.entity.speed
        if self.entity.pose.y == self.target[1]:
            self.entity.shift_y = 0

        return 1

class GOTOBehaviour(Behaviour):
    def __init__(self, entity, env, specific_target):
        super(GOTOBehaviour, self).__init__(entity, env)
        self.specific_target = specific_target

        self.state = "Goto"
        self.label = "GT"

    def setSpecificTarget(self, st):
        self.specific_target = st

    def computePath(self):
        del self.path[:]
        super(GOTOBehaviour, self).computePath(self.specific_target)

    def nextStep(self):
        ns = super(GOTOBehaviour, self).nextStep()
        return ns

        

        




