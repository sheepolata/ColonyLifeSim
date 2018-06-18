import utils.utils as utils
import utils.basic_colors as basic_colors
import behaviours.behaviour as behaviour
import random
import sprites.sprite
import profilerConfig as pc
import utils.pathfinding as pf

import threading

import time
import math
import copy

import pygame

class Entity(threading.Thread):
    def __init__(self, env):
        super(Entity, self).__init__()
        self.daemon = True

        self.name = "Entity"

        self.pose = utils.Pose(0, 0)
        self.env = env

        self.behaviour = None

        self.dead = False
        self.paused = False
        self.user_paused = False

        self.running = True

        self.sprite = sprites.sprite.SpriteEntityBase(basic_colors.CYAN, self.pose)

    def setPose(self, x, y):
        self.pose.x = x
        self.pose.y = y
        self.sprite = sprites.sprite.SpriteEntityBase(basic_colors.CYAN, self.pose)

    def wait(self):
        # time.sleep(t)
        self.wait()

    def getPose(self):
        return self.pose.getPose()

    def setRandomPose(self, maxx, maxy):
        self.pose.setPose(random.randint(0, maxx), random.randint(0, maxy))

    def run(self):
        while self.running:
            if not self.user_paused and not self.paused:
                self.update()
            ttw = 1.0/float(pc.get("FORCED_FPS")) if pc.get("FORCED_FPS") != 0 else 1
            time.sleep(ttw)

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def user_pause(self):
        self.user_paused = True

    def user_resume(self):
        self.user_paused = False

    def stop(self):
        self.running = not self.running

    def update(self):
        # self.pose.setPose(x, y)
        self.sprite.update(self.pose)

    def die(self):
        print(self.name, "killed")

        self.dead = True
        self.resume()
        self.user_resume()
        self.stop()

    def drawDebugCollision(self, surface):
        pass

class NPC(Entity):
    def __init__(self, env, name="NPC"):
        super(NPC, self).__init__(env)
        #Basic
        self.name = name

        self.shift_x = 0
        self.shift_y = 0
        self.speed = round(random.random()*0.6, 2) + 0.4

        self._tick = 0

        self.target_res = None

        self.selected = False

        self.neigh_computation_thread = None
        self.closestfood_computation_thread = None

        self.count_check_availaible_food = 0
        self.count_check_availaible_food_period = 50

        #Inventory
        self.bagpack = {}

        #vital monitoring
        self.hunger = 0.0
        self.hunger_thresh = random.randint(60, 80)
        self.hunger_max = self.hunger_thresh + 30
        self.have_to_eat = False

        self.harvester = random.random()*0.8 + 0.4

        self.vision_radius = 150

        #MEMORY and SOCIAL

        self.neighbours = []
        self.neighbours_rect = []
        self.memory = random.randint(800, 1200)
        self.known_food = {}

        #cowardliness 0 ... 10 courage
        # self.courage = round(random.random()*10, 2)
        self.courage = random.choice([0, 1])
        #kindness 0 ... 10 aggressivness
        # self.kindness = round(random.random()*10, 2)
        self.kindness = random.choice([0, 1])

        #graphics
        self.sprite = sprites.sprite.SpriteNPC(basic_colors.CYAN, self.pose, self)

    def setNeigh_computation_thread(self, NCT):
        self.neigh_computation_thread = NCT

    def setClosestfood_computation_thread(self, CFCT):
        self.closestfood_computation_thread = CFCT

    def init(self):
        self._ticker = utils.perpetualTimer(1, self.tick)
        self._ticker.start()

    def isFriend(self, other):
        return other.kindness == self.kindness

    def computeNeighbours(self):
        self.neighbours = self.neigh_computation_thread.neighbours[self]

    def updateFoodMemory(self):
        torm = []
        for k in self.known_food.keys():
            self.known_food[k] += 1
            if self.known_food[k] >= self.memory:
                torm.append(k)
        for k in torm:
            del self.known_food[k]

    def computeKnownFood(self):
        for cf in self.closestfood_computation_thread.closestFood[self]:
            self.known_food[cf] = 0

        # for f in self.env.ressources["food"]:
        #     if not pf.checkStraightPath(self.env, self.getPose(), f.getPose(), 10, check_river=False) and utils.distance2p(self.getPose(), f.getPose()) <= self.vision_radius:
        #         self.known_food[f] = 0

    def tick(self):

        if self._tick%10 == 0:
            self.env.pgo_obj.updatePosition(self)

        if self.hunger <= self.hunger_max*0.1:
            self.have_to_eat = False
        elif self.hungry():
            self.have_to_eat = True

        if self._tick%50 == 0:
            self.hunger += round((random.random() * 0.25) + 0.25, 2)
            if self.hunger >= self.hunger_max:
                self.die()

        self.updateFoodMemory()
        if self._tick%50 == 0:
            self.computeNeighbours()
            self.computeKnownFood()

        self._tick += 1
        if self._tick%1000 == 0:
            self._tick = 0

    def collectRessource(self, res):
        if not res.name in self.bagpack.keys():
            self.bagpack[res.name] = 0

        v = res.getSome(random.randint(25, 45)) 
        self.bagpack[res.name] = round(v * self.harvester, 2)
        # print("collect", v * self.harvester)
        return round(10*v) #Time to wait

    def haveFood(self):
        return "food" in self.bagpack.keys() and self.bagpack["food"] > 0

    def consumeFood(self):
        if self.haveFood():
            consume = 1 if self.bagpack["food"] >= 1 else self.bagpack["food"]
            self.hunger -= consume
            self.bagpack["food"] -= consume
        if self.hunger <= 0:
            self.hunger = 0

    def setIdleBehaviour(self):
        self.pause()
        if self.behaviour!= None and self.behaviour.state == "idle":
            return
        self.behaviour = None
        self.behaviour = behaviour.IdleBehaviour(self, self.env)
        self.behaviour.computePath()
        self.resume()

    def setGOTOBehaviour(self, st):
        self.pause()
        self.behaviour = None
        self.behaviour = behaviour.GOTOBehaviour(self, self.env, st)
        cp = self.behaviour.computePath()
        self.resume()


    def setGOTORessource(self, res):
        self.pause()
        self.behaviour = None
        self.behaviour = behaviour.GOTORessource(self, self.env, res)
        cp = self.behaviour.computePath()
        self.resume()

    def setHarvestBehaviour(self, res):
        self.pause()
        self.behaviour = None
        self.behaviour = behaviour.Harvest(self, self.env, res)
        self.behaviour.computePath()
        self.resume()

    def setWaitBehaviour(self, time):
        self.pause()
        self.behaviour = None
        self.behaviour = behaviour.Wait(self, self.env, time)
        self.behaviour.computePath()
        self.resume()

    def setEmptyBehaviour(self):
        self.pause()
        self.behaviour = None
        self.behaviour = behaviour.EmptyBehaviour(self, self.env)
        self.resume()

    def setRandomPose(self, maxx, maxy):
        super(NPC, self).setRandomPose(maxx, maxy)
        while self.env.collideOneObstacle_Point(self.getPose()):
            super(NPC, self).setRandomPose(maxx, maxy)
            
    def setCollectFoodBehaviour(self):
        self.pause()
        self.behaviour = None
        self.behaviour = behaviour.CollectFood(self, self.env)
        self.resume()

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

        if self.have_to_eat:
            # print self.behaviour.label

            # if self.selected:
            #     print self.name + " have to eat"

            if self.haveFood():
                self.consumeFood()
            elif self.behaviour.label != "COFO":
                if self.count_check_availaible_food == 0:
                    res, _tar_res = self.env.getClosestRessourceFromList(self.getPose(), self.known_food.keys())
                    if res != None:
                        self.count_check_availaible_food = 0
                        self.count_check_availaible_food_period = 50
                        self.setCollectFoodBehaviour()
                    else:
                        self.count_check_availaible_food_period = min(self.count_check_availaible_food_period+50, 1500)

                self.count_check_availaible_food = (self.count_check_availaible_food + 1) % self.count_check_availaible_food_period

        # print(self.name, "update", self.behaviour.state)
        if self.behaviour != None and self.behaviour.state != "empty" and self.behaviour.state != "nothing":
            ns = self.behaviour.nextStep()
            # print ns
            if ns == -1:
                self.setIdleBehaviour()
            elif self.behaviour.state == "goto" and ns == 1:
                self.setIdleBehaviour()
            elif self.behaviour.label == "COFO" and ns == 1:
                self.setIdleBehaviour()
            elif self.behaviour.state == "wait" and ns == 1:
                self.setIdleBehaviour()
            elif self.behaviour.state == "idle" and ns == 1:
                self.setWaitBehaviour(50)
        else:
            self.setIdleBehaviour()
 
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
    def __init__(self, env, name, value, rep, spawner=None):
        super(Ressource, self).__init__(env)
        self.name = name

        self._tick = 0

        self.used = False

        self.spawner = spawner

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

        self.rect = env.getCurrentRect(self.getPose())

        self.sprite = sprites.sprite.SpriteRessource(self, self.pose)

        self.env.pgo_obj.updateFoodPosition(self)
        
    def setRegrowBehaviour(self):
        self.behaviour = behaviour.RegrowBehaviour(self, self.env, 50)

    def setPose(self, x, y):
        super(Ressource, self).setPose(x, y)
        self.rect = env.getCurrentRect(self.getPose())
        self.sprite = sprites.sprite.SpriteRessource(self, self.pose)

        self.env.pgo_obj.updateFoodPosition(self)

    def update(self):
        self._tick = (self._tick+1)%1000
        if self._tick%500 == 0:
            self.env.pgo_obj.updateFoodPosition(self)


        if self.behaviour != None:
            ns = self.behaviour.nextStep()
        super(Ressource, self).update()

    def regrow(self):
        if self.replenishable:
            self.value = self.value + self.replen_rate if self.value + self.replen_rate <= self.max_value else self.max_value
            if not self.harvestable and self.value >= (self.max_value/5.0):
                self.harvestable = True
        elif self.value <= 0:
            self.die()

    def getSome(self, factor):
        v = round(factor, 2) 
        v = v if self.value >= v else self.value
        self.value -= v
        if self.value <= 0:
            self.harvestable = False
        return v
        
class Spawner(Entity):
    def __init__(self, env, name, sp_type, maxs, period, factor, rep):
        super(Spawner, self).__init__(env)
        self.name = name
        self.sp_type = sp_type

        self.factor = factor

        self.period = period
        self.radius = 25

        self.max_spawnee = maxs
        self.current_spawnee = 0
        self.list_ressource = []

        self.rect = env.getCurrentRect(self.getPose())

        self.angle = (float(2*math.pi) / self.max_spawnee)

        self.replenishable = rep

        self.sprite = sprites.sprite.SpriteSpawner(self, self.pose)
    
    def setRandomPose(self, maxx, maxy):
        # super(Spawner, self).setRandomPose(maxx, maxy)
        self.pose.setPose(random.randint(int(self.radius*1.2), maxx - int(self.radius*1.2))
                            , random.randint(int(self.radius*1.2), maxy - int(self.radius*1.2)))
        while self.env.getCurrentRect(self.getPose()) == None or self.env.collideOneObstacle_Point(self.getPose()):
            super(Spawner, self).setRandomPose(maxx, maxy)

    def start(self):
        super(Spawner, self).start()

    def die(self):
        super(Spawner, self).die()

    def setPose(self, x, y):
        super(Spawner, self).setPose(x, y)
        self.rect = self.env.getCurrentRect(self.getPose())
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

    def spawn(self, start_thread=True):
        if self.sp_type == "foodspawner":
            res = Ressource(self.env, "food", random.randint(int(20*self.factor), int(75*self.factor)), self.replenishable, spawner=self)

            current_angle = self.angle * self.current_spawnee
            current_radius = random.randint(int(self.radius*0.2), self.radius)
            npx = self.pose.x + current_radius * math.cos(current_angle)
            npy = self.pose.y + current_radius * math.sin(current_angle)
            asser = self.env.getCurrentRect((npx, npy))
            while asser == None:
                self.radius = int(self.radius * 1.05)
                current_angle += math.pi / 12
                current_radius = random.randint(int(self.radius*0.2), self.radius)
                npx = self.pose.x + current_radius * math.cos(current_angle)
                npy = self.pose.y + current_radius * math.sin(current_angle)

                asser = self.env.getCurrentRect((npx, npy))

            res.pose.x = npx
            res.pose.y = npy

            res.setRegrowBehaviour()
            self.env.addRessource(res)
            self.list_ressource.append(res)
            self.current_spawnee += 1

            if start_thread : res.start()     