import utils.utils as utils
import utils.basic_colors as basic_colors
import behaviours.behaviour as behaviour
import random
import sprites.sprite 

import pygame

class Entity(object):
    def __init__(self, env):
        self.name = "Entity"

        self.pose = utils.Pose(0, 0)
        self.env = env

        self.behaviour = None

        self.dead = False

        self.sprite = sprites.sprite.SpriteEntityBase(basic_colors.CYAN, self.pose)

    def setPose(self, x, y):
        self.pose.x = x
        self.pose.y = y
        self.sprite = sprites.sprite.SpriteEntityBase(basic_colors.CYAN, self.pose)


    def getPose(self):
        return self.pose.getPose()

    def setRandomPose(self, maxx, maxy):
        self.pose.setPose(random.randint(0, maxx), random.randint(0, maxy))

    def update(self):
        # self.pose.setPose(x, y)
        self.sprite.update(self.pose)

    def die(self):
        print(self.name, "killed")

        self.dead = True

    def drawDebugCollision(self, surface):
        pass

class NPC(Entity):
    def __init__(self, env, name="NPC"):
        super(NPC, self).__init__(env)
        #Basic
        self.name = name

        self.shift_x = 0
        self.shift_y = 0
        self.speed = 1

        self._tick = 0

        self.target_res = None

        #Inventory
        self.bagpack = {}

        #vital monitoring
        self.hunger = 0.0
        self.hunger_thresh = random.randint(40, 60)
        self.hunger_max = self.hunger_thresh + 50
        self.have_to_eat = False

        self.harvester = random.random()*0.5 + 0.75

        #graphics
        self.sprite = sprites.sprite.SpriteNPC(basic_colors.CYAN, self.pose, self)

        # self.init()

    def init(self):
        self._ticker = utils.perpetualTimer(1, self.tick)
        self._ticker.start()

    def tick(self):
        if self._tick%50 == 0:

            self.hunger += round((random.random() * 0.25) + 0.25, 2)
            if self.hunger >= self.hunger_max:
                self.die()

        self._tick += 1
        if self._tick%1000 == 0:
            self._tick = 0

    def collectRessource(self, res):
        if not res.name in self.bagpack.keys():
            self.bagpack[res.name] = 0

        self.bagpack[res.name] = res.getSome(self, 5)

    def haveFood(self):
        return "food" in self.bagpack.keys() and self.bagpack["food"] > 0

    def consumeFood(self):
        if self.haveFood():
            consume = 1 if self.bagpack["food"] >= 1 else self.bagpack["food"]
            self.hunger -= consume
            self.bagpack["food"] -= consume
        if self.hunger <= 0:
            self.hunger = 0
            self.have_to_eat = False

    def setIdleBehaviour(self):
        if self.behaviour!= None and self.behaviour.state == "idle":
            return
        self.behaviour = None
        self.behaviour = behaviour.IdleBehaviour(self, self.env)
        self.behaviour.computePath()

    def setGOTOBehaviour(self, st):
        self.behaviour = None
        self.behaviour = behaviour.GOTOBehaviour(self, self.env, st)
        cp = self.behaviour.computePath()


    def setGOTORessource(self, res):
        self.behaviour = None
        self.behaviour = behaviour.GOTORessource(self, self.env, res)
        cp = self.behaviour.computePath()

    def setHarvestBehaviour(self, res):
        self.behaviour = None
        self.behaviour = behaviour.Harvest(self, self.env, res)
        self.behaviour.computePath()

    def setWaitBehaviour(self, time):
        self.behaviour = None
        self.behaviour = behaviour.Wait(self, self.env, time)
        self.behaviour.computePath()

    def setEmptyBehaviour(self):
        self.behaviour = None
        self.behaviour = behaviour.EmptyBehaviour(self, self.env)

    def setRandomPose(self, maxx, maxy):
        super(NPC, self).setRandomPose(maxx, maxy)
        while self.env.collideOneObstacle_Point(self.getPose()):
            super(NPC, self).setRandomPose(maxx, maxy)
            

    def drawDebugCollision(self, surface):
        super(NPC, self).drawDebugCollision(surface)
        for c in filter(lambda a: a != None, self.behaviour.collision_debug):
            pygame.draw.circle(surface, basic_colors.ALPHA_RED, c, 3)

    def hungry(self):
        return self.hunger >= self.hunger_thresh

    def update(self):
        self.tick() 

        if self.dead:
            return

        if self.hungry():
            self.have_to_eat = True

        if self.have_to_eat:
            if self.haveFood():
                self.consumeFood()
            else:
                target_res_tmp = self.env.getClosestRessource(self.getPose(), "food")
                if target_res_tmp == None:
                    if self.behaviour.state != "idle":
                        self.setIdleBehaviour()
                elif self.behaviour.state != "wait":
                    if self.behaviour.state == "gotoressource" and self.behaviour.count == 0:
                        if target_res_tmp != self.target_res:
                            self.target_res = target_res_tmp
                            self.setGOTORessource(self.target_res)
                    if self.behaviour.state != "gotoressource" and self.behaviour.state != "harvest":
                        self.target_res = target_res_tmp
                        if utils.near(self.getPose(), self.target_res.getPose(), _thresh=15):
                            self.setHarvestBehaviour(self.target_res)
                        else:
                            self.setGOTORessource(self.target_res)

        # print(self.name, "update", self.behaviour.state)
        if self.behaviour != None and self.behaviour.state != "empty" and self.behaviour.state != "nothing":
            ns = self.behaviour.nextStep()
            if ns == -1:
                self.setIdleBehaviour()
            elif self.behaviour.state == "goto" and ns == 1:
                self.setIdleBehaviour()
            elif self.behaviour.state == "gotoressource" and ns == 1:
                self.setHarvestBehaviour(self.target_res)
            elif self.behaviour.state == "harvest" and ns == 1:
                self.setWaitBehaviour(35)
            elif self.behaviour.state == "wait" and ns == 1:
                self.setIdleBehaviour()
            elif self.behaviour.state == "idle" and ns == 1:
                self.setWaitBehaviour(50)
 
        self.pose.x += self.shift_x
        self.pose.y += self.shift_y
        super(NPC, self).update()
        

    def setPose(self, x, y):
        super(NPC, self).setPose(x, y)
        self.sprite = sprites.sprite.SpriteNPC(basic_colors.CYAN, self.pose, self)


class Obstacle(Entity):
    def __init__(self, sizew, sizeh, env):
        super(Obstacle, self).__init__(env)
        
        self.sizew = sizew

        self.sizeh = sizeh

        self.sprite = sprites.sprite.SpriteObstacle(basic_colors.MAROON, self.pose, self.sizew, self.sizeh)
        
    def setRandomPose(self, maxx, maxy):
        super(Obstacle, self).setRandomPose(maxx, maxy)
        self.sprite.rect = pygame.Rect(self.sprite.pose.x-(self.sprite.sizew/2), self.sprite.pose.y-(self.sprite.sizeh/2), self.sprite.sizew, self.sprite.sizeh)

class Ressource(Entity):
    """docstring for Ressource"""
    def __init__(self, env, name, value, rep):
        super(Ressource, self).__init__(env)
        self.name = name

        self.used = False

        self.max_value = round(value*2.5, 2)
        if rep:
            self.value = value
        else:
            self.value = self.max_value

        self.replenishable = rep
        self.replen_rate = round(random.random()*0.45 + 0.33, 2)
        self.harvestable = True

        randpose = self.env.getRandomValidPose()
        self.pose = utils.Pose(randpose[0], randpose[1])

        self.sprite = sprites.sprite.SpriteRessource(self, self.pose)
        
    def setRegrowBehaviour(self):
        self.behaviour = behaviour.RegrowBehaviour(self, self.env)

    def setWaitBehaviour(self, time):
        self.behaviour = None
        self.behaviour = behaviour.Wait(self, self.env, time)

    def setPose(self, x, y):
        super(Ressource, self).setPose(x, y)
        self.sprite = sprites.sprite.SpriteRessource(self, self.pose)

    def update(self):
        if self.behaviour != None and self.behaviour.state != "empty" and self.behaviour.state != "nothing":
            ns = self.behaviour.nextStep()
            if self.behaviour.state == "regrow" and ns == 1:
                self.setWaitBehaviour(50)
            elif self.behaviour.state == "wait" and ns == 1:
                self.setRegrowBehaviour()
        super(Ressource, self).update()

    def regrow(self):
        if self.replenishable:
            self.value = self.value + self.replen_rate if self.value + self.replen_rate <= self.max_value else self.max_value
            if not self.harvestable and self.value >= (self.max_value/5.0):
                self.harvestable = True
        elif self.value <= 0:
            self.die()

    def getSome(self, npc, factor):
        v = round(factor * npc.harvester, 2) 
        v = v if self.value >= v else self.value
        self.value -= v
        if self.value <= 0:
            self.harvestable = False
        return v
        
class Spawner(Entity):
    def __init__(self, env, name, sp_type, period, factor):
        super(Spawner, self).__init__(env)
        self.name = name
        self.sp_type = sp_type

        self.factor = factor

        self.period = period
        self.radius = 30

        self.max_spawnee = random.randint(8, 12)
        self.current_spawnee = 0

        self.list_ressource = []

        self.sprite = sprites.sprite.SpriteSpawner(self, self.pose)
    
    def setRandomPose(self, maxx, maxy):
        super(Spawner, self).setRandomPose(maxx, maxy)
        while self.env.getCurrentRect(self.getPose()) == None or self.env.collideOneObstacle_Point(self.getPose()):
            super(Spawner, self).setRandomPose(maxx, maxy)

    def setPose(self, x, y):
        super(Ressource, self).setPose(x, y)
        self.sprite = sprites.sprite.SpriteSpawner(self, self.pose)

    def setSpawnerBehaviour(self):
        self.behaviour = None
        self.behaviour = behaviour.SpawnerBehaviour(self, self.env, self.period)

    def update(self):
        for r in self.list_ressource:
            if r.dead :
                self.list_ressource.remove(r)
                self.current_spawnee -= 1
        ns = self.behaviour.nextStep()
        if ns == 1:
            self.spawn()
            # print(str(self.current_spawnee) + "/" + str(self.max_spawnee))
        super(Spawner, self).update()

    def spawn(self):
        if self.sp_type == "foodspawner":
            res = Ressource(self.env, "food", random.randint(int(20*self.factor), int(30*self.factor)), False)

            npx = random.randint(self.pose.x - self.radius, self.pose.x + self.radius)
            npy = random.randint(self.pose.y - self.radius, self.pose.y + self.radius)
            asser = self.env.getCurrentRect((npx, npy))
            while asser == None:
                # print "asser false"
                npx = random.randint(self.pose.x - self.radius, self.pose.x + self.radius)
                npy = random.randint(self.pose.y - self.radius, self.pose.y + self.radius)
                asser = self.env.getCurrentRect((npx, npy))

            res.pose.x = npx
            res.pose.y = npy

            res.setRegrowBehaviour()
            self.env.addRessource(res)
            self.list_ressource.append(res)
            self.current_spawnee += 1
        