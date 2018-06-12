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
        self.ipath_prev = -1
        self.k = 0

        self.state = "nothing"
        self.label = "NAN"

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
            return

        self.target = _target

        self.path.append(self.entity.getPose())

        #if line from entity.pos to target is OK, do not compute astar
            #y = a*x + b => a==0 : parallele; a==inf : perpendicular; a == (-)1 : (-)45deg
        a, b = geo.computeLineEquation(current_rect.center, target_rect.center)
        astar_needed = False
        if a == None or b == None:
            astar_needed = True
        elif abs(current_rect.center[0] - target_rect.center[0]) > abs(current_rect.center[1] - target_rect.center[1]):
            mini = min(current_rect.center[0], target_rect.center[0])
            maxi = max(current_rect.center[0], target_rect.center[0])

            for step_x in range(mini, maxi, 15):
                y = a*step_x + b
                if self.env.collideOneObstacle_Point((step_x, y)):
                    astar_needed = True
        else:
            mini = min(current_rect.center[1], target_rect.center[1])
            maxi = max(current_rect.center[1], target_rect.center[1])

            for step_y in range(mini, maxi, 15):
                # y = a*step_x + b
                x = (step_y - b)/a
                if self.env.collideOneObstacle_Point((x, step_y)):
                    astar_needed = True

        #else compute astar
        if astar_needed:
            path_astar = pf.astar(current_rect.center, target_rect.center , self.env)

            if path_astar == None :
                print("Error, no path found")
                return -1
            for p in reversed(path_astar):
                self.path.append(p)

        self.path.append(self.target)
        return 1

    def nextStep(self):
        if not self.path:
            return 1
        if self.ipath >= len(self.path):
            return 1



        self.target = self.path[self.ipath]


        if utils.near(self.entity.getPose(), self.target, _thresh=self.entity.speed + 1):
            self.ipath_prev = self.ipath
            self.ipath += 1
            self.entity.shift_x = 0
            self.entity.shift_y = 0
            if self.ipath >= len(self.path):
                self.ipath = 0
                self.ipath_prev = -1
                del self.path[:]
            return 0

        p1 = self.entity.getPose()
        p2 = self.target

        if self.ipath_prev != self.ipath:
            self.k = float(self.entity.speed) / float(utils.distance2p(p1, p2))
        new_p = ( self.k * p2[0] + (1-self.k)*p1[0] , self.k * p2[1] + (1-self.k)*p1[1] )

        self.entity.shift_x = new_p[0] - self.entity.pose.x
        self.entity.shift_y = new_p[1] - self.entity.pose.y

        return 0

    def getPath(self):
        return self.path[self.ipath]

class EmptyBehaviour(Behaviour):
    def __init__(self, entity, env):
        super(EmptyBehaviour, self).__init__(entity, env)
        self.state = "empty"
        self.label = "EMP"
    def computePath(self):
        return 1

    def nextStep(self):
        return 1
        

class IdleBehaviour(Behaviour):
    def __init__(self, entity, env):
        super(IdleBehaviour, self).__init__(entity, env)

        self.state = "idle"
        self.label = "I"

        self.collision_debug = []

    def computePath(self):
        del self.path[:]
        self.path.append(self.entity.getPose())

        rdspan = 40

        tx = self.entity.getPose()[0] + random.randint(-rdspan, rdspan)
        ty = self.entity.getPose()[1] + random.randint(-rdspan, rdspan)

        rect_temp = self.env.getCurrentRect((tx, ty))
        rect_ent_temp = self.env.getCurrentRect(self.entity.getPose())
        if(rect_temp != None and rect_ent_temp 
            and pf.getPathLength(self.env, rect_ent_temp.center, 
                rect_temp.center) <= 175
            ):
            _target = (tx, ty)

            return super(IdleBehaviour, self).computePath(_target)
        else: 
            return -1

    def nextStep(self):
        ns = super(IdleBehaviour, self).nextStep()
        if ns == 1:
            self.computePath()
        return ns

class GOTOBehaviour(Behaviour):
    def __init__(self, entity, env, specific_target):
        super(GOTOBehaviour, self).__init__(entity, env)
        self.specific_target = specific_target

        self.state = "goto"
        self.label = "GT"

        self.count = 0

    def setSpecificTarget(self, st):
        self.specific_target = st

    def computePath(self):
        del self.path[:]
        return super(GOTOBehaviour, self).computePath(self.specific_target)

    def nextStep(self):
        self.count = (self.count+1) % 100
        return super(GOTOBehaviour, self).nextStep()


class GOTORessource(GOTOBehaviour):
    def __init__(self, entity, env, ressource):
        self.ressource = ressource
        super(GOTORessource, self).__init__(entity, env, self.ressource.getPose())

        self.state = "gotoressource"
        self.label = "GTR"

    def nextStep(self):
        return super(GOTORessource, self).nextStep()

class Wait(Behaviour):
    def __init__(self, entity, env, clock):
        super(Wait, self).__init__(entity, env)
        self.clock = clock

        self.state = "wait"
        self.label = "W"

    def computePath(self):
        return 1

    def nextStep(self):
        self.clock -= 1
        if self.clock <= 0:
            return 1
        return 0

class SpawnerBehaviour(Behaviour):
    def __init__(self, entity, env, period):
        super(SpawnerBehaviour, self).__init__(entity, env)
        self.period = period
        self.count = 0

        self.state = "spawner"
        self.label = "SPWN"

    def computePath(self):
        return 1

    def nextStep(self):
        self.count = (self.count+1) % self.period
        if self.count == 0 and self.entity.current_spawnee < self.entity.max_spawnee:
            return 1
        return 0
                        

class Harvest(Behaviour):
    def __init__(self, entity, env, res):
        super(Harvest, self).__init__(entity, env)
        self.entity = entity
        self.env = env
        self.res = res

        self.state = "harvest"
        self.label = "HAR"

    def computePath(self):
        return 1

    def nextStep(self):
        if self.res == None or not utils.near(self.entity.getPose(), self.res.getPose(), _thresh=15):
            return -1

        self.entity.collectRessource(self.res)

        return 1
        
class RegrowBehaviour(Behaviour):
    def __init__(self, res, env):
        super(RegrowBehaviour, self).__init__(res, env)

        self.state = "regrow"
        self.label = "REG"

    def computePath(self):
        return 1

    def nextStep(self):
        self.entity.regrow()
        return 1