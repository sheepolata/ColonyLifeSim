import random

import utils.utils as utils
import utils.geometry as geo
import utils.pathfinding as pf

import time

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

        self.cooldown = 0

    def computePath(self, _target, _target_rect=None):

        current_rect = self.env.getCurrentRect(self.entity.getPose())
        while current_rect == None:
            self.entity.setPose(self.entity.getPose()[0] + random.randint(-4, 4), self.entity.getPose()[1]+ random.randint(-4, 4))
            current_rect = self.env.getCurrentRect(self.entity.getPose())
        # return -1

        if _target_rect == None:
            target_rect = self.env.getCurrentRect(_target)
            trial = 0
            if target_rect == None:
                return -1
        else:
            target_rect = _target_rect

        self.target = _target

        self.path.append(self.entity.getPose())

        astar_needed = pf.checkStraightPath(self.env, current_rect.center, target_rect.center, int(round(self.entity.speed))+1)
        #else compute astar
        if astar_needed:
            path_astar = pf.astar(current_rect.center, target_rect.center , self.env)

            if path_astar == None :
                print("Error, no path found")
                return -1
            for p in reversed(path_astar):
                self.path.append(p)

        # print self.target
        self.path.append(self.target)
        # print self.path
        return 1

    def nextStep(self):
        if not self.path:
            return 1
        if self.ipath >= len(self.path):
            return 1



        self.target = self.path[self.ipath]

        # print self.target
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

            return super(IdleBehaviour, self).computePath(_target, None)
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

    def computePath(self, _target_rect=None):
        del self.path[:]
        return super(GOTOBehaviour, self).computePath(self.specific_target, _target_rect=_target_rect)

    def nextStep(self):
        self.count = (self.count+1) % 150
        return super(GOTOBehaviour, self).nextStep()

class GOTORessource(GOTOBehaviour):
    def __init__(self, entity, env, ressource):
        self.ressource = ressource
        super(GOTORessource, self).__init__(entity, env, self.ressource.getPose())

        self.state = "gotoressource"
        self.label = "GTR"

    def computePath(self, _target_rect=None):
        return super(GOTORessource, self).computePath(_target_rect=_target_rect)

    def nextStep(self):
        return super(GOTORessource, self).nextStep()

class CollectFood(Behaviour):
    def __init__(self, entity, env):
        super(CollectFood, self).__init__(entity, env)

        self.state = "collectfood"
        self.label = "COFO"

        self.count_recomp_path = 0

        self.gotobehaviour = None
        self.harvestbehaviour = None
            
        self.entity.target_res = None

    def computePath(self):
        pass    

    def nextStep(self):
        self.count_recomp_path = (self.count_recomp_path+1)%360

        changed = False
        _target_rect = None
        if self.entity.target_res == None or not self.entity.target_res.harvestable:
            changed = True

            self.entity.target_res, _target_rect = self.env.getClosestRessourceFromList(self.entity.getPose(), self.entity.known_food)
            
            if self.entity.target_res == None:
                return 1
            self.gotobehaviour = GOTORessource(self.entity, self.env, self.entity.target_res)
            self.state = "collectfood:GTR"
        elif self.count_recomp_path == -1:
            old_tr, _target_rect = self.env.getClosestRessourceFromList(self.entity.getPose(), "food", approx=False)
            
            if self.entity.target_res != None and old_tr != None and self.entity.target_res != old_tr:
                changed = True
                self.entity.target_res = old_tr
                self.gotobehaviour = GOTORessource(self.entity, self.env, self.entity.target_res)
                self.state = "collectfood:GTR"
                

        if changed:
            self.gotobehaviour.computePath(_target_rect=_target_rect)
            self.path = self.gotobehaviour.path
            changed = False

        if self.gotobehaviour != None:
            ns = self.gotobehaviour.nextStep()
            if ns == 1:
                self.gotobehaviour = None
                self.harvestbehaviour = Harvest(self.entity, self.env, self.entity.target_res)
                self.harvestbehaviour.computePath()
                self.path = self.harvestbehaviour.path

                self.state = "collectfood:HAR"
                return 0
            else:
                return 0
        elif self.harvestbehaviour != None:
            ns = self.harvestbehaviour.nextStep()
            if ns == 1:
                self.harvestbehaviour = None
                return 1
            else:
                return 0
        else:
            return -1

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

class ConsumeFood(Behaviour):
    def __init__(self, entity, env):
        super(ConsumeFood, self).__init__(entity, env)
        self.entity = entity
        self.env = env

        self.state = "consumeFood"
        self.label = "EAT"

        self.count = -1
        self.ttw = 0

    def computePath(self):
        self.path = []
        return 1

    def nextStep(self):
        if self.count == -1:
            self.ttw = self.entity.consumeFood()
        elif self.count <= 0:
            self.count = -1
            return 1
        else:
            self.count -= 1
            return 0

        
class Harvest(Behaviour):
    def __init__(self, entity, env, res):
        super(Harvest, self).__init__(entity, env)
        self.entity = entity
        self.env = env
        self.res = res

        self.count = -1
        self.qtt = 0

        self.state = "harvest"
        self.label = "HAR"

    def computePath(self):
        self.path = []
        return 1

    def nextStep(self):
        if self.res == None:
            return -1
        
        if self.count == -1:
            self.qtt = self.entity.collectRessource(self.res)
            self.count = self.qtt * self.res.time_per_unit
            # print "harvest begin"
            return 0
        elif self.count <= 0:
            # print "harvest over"
            self.entity.putInBagpack(self.res, self.qtt)
            self.count = -1
            return 1
        else:
            self.count -= 1
            # print self.count
            return 0
        
class SocialInteraction(Behaviour):
    def __init__(self, entity, env, other):
        super(SocialInteraction, self).__init__(entity, env)
        self.other = other

        self.state = "socialinteraction"
        self.label = "SOCINT"

        self.time_taken = 150

        self.cooldown = 300

    def computePath(self):
        return 1

    def nextStep(self):
        if self.time_taken > 0:
            self.time_taken -= 1
            return 0
        elif self.time_taken <= 0:
            self.entity.socialInteraction(self.other)
            return 1

        

class RegrowBehaviour(Behaviour):
    def __init__(self, res, env, period):
        super(RegrowBehaviour, self).__init__(res, env)

        self.state = "regrow"
        self.label = "REG"

        self.period = period
        self.count = 0

    def computePath(self):
        return 1

    def nextStep(self):
        self.count += 1
        if self.count%self.period == 0:
            self.entity.regrow()
        return 1