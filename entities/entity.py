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
        # print(self.name, "killed")

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

        self.no_social_interaction = 0

        #Inventory
        self.bagpack = {}

        #vital monitoring
        self.hunger = 0.0
        self.hunger_thresh = random.randint(60, 80)
        self.hunger_max = self.hunger_thresh + 30
        self.have_to_eat = False

        self.harvester = random.random()*0.8 + 0.4

        self.social = random.random()*0.8 + 0.4

        self.vision_radius = 150

        self.level = 0
        self.global_xp = 0
        self.global_xp_next_lvl = 100

        #MEMORY and SOCIAL
        self.last_social_interaction = "None"

        self.interaction_range = 110

        self.neighbours = []
        self.neighbours_rect = []

        self.social_xp = {}
        self.social_cooldown = 0

        self.memory = random.randint(800, 1200)
        self.known_food = {}

        #cowardliness 0 ... 10 courage
        self.courage_min = 0
        self.courage_max = 10
        self.courage = random.randint(self.courage_min, self.courage_max)
        # self.courage = random.choice([0, 1])

        #aggressivness 0 ... 10 kindness
        self.kindness = random.randint(0, 10)
        # self.kindness = random.choice([0, 1])

        #Attack
        self.will_attack = False
        self.attack_target = None

        self.attack_range = 30

        self.attack = (self.courage) + 3
        
        self.str_min = 0
        self.str_max = 5
        self.strength = random.randint(self.str_min, self.str_max) + int(round(self.courage * 0.33))
        self.attack_damage = int(round(self.strength * 1.2))

        self.attack_dice = [1, 4]

        #Defense
        self.hitpoint_max = 100
        self.hitpoint = self.hitpoint_max

        self.defense = 10 + (self.courage_max - self.courage) + int(round(self.strength * 0.33))

        #graphics
        self.sprite = sprites.sprite.SpriteNPC(basic_colors.CYAN, self.pose, self)

    def level_up(self):
        self.level += 1

        self.global_xp = self.global_xp%int(self.global_xp_next_lvl)
        self.global_xp_next_lvl = int(round(self.global_xp_next_lvl * 1.10))

        if random.random() < 0.5:
            self.hitpoint_max += 10
            self.hitpoint += 10
        if random.random() < 0.38:
            self.memory += 50
        if random.random() < 0.3:
            self.strength += 1
        if random.random() < 0.18:
             self.harvester += 0.05 
        if random.random() < 0.18:
            self.social += 0.05 
        if random.random() < 0.15:
            self.attack += 1
        if random.random() < 0.1:
            self.attack_dice[1] += 1
        if random.random() < 0.05:
            self.attack_dice[0] += 1

        #update values
        self.attack_damage = int(round(self.strength * 1.2))
        self.defense = 10 + (self.courage_max - self.courage) + int(round(self.strength * 0.33))

    def getAttackProbability(self):
        vmax = self.courage_max*1.33 + self.str_max + self.hitpoint_max
        vmin = self.courage_min*1.33 + self.str_min + self.hitpoint_max

        vcurr = self.courage + self.strength + self.hitpoint

        return utils.normalise(vcurr, vmin, vmax)
        
    def setInitialSocialXP(self):
        for npc in self.env.npcs:
            self.social_xp[npc] = 0

    def getInteractionProbability(self, other):
        diff_kind = float(abs(self.kindness - other.kindness) + 1)

        if self.isGoodFriend(other):
            nature = "good"
            proba = ((1 / diff_kind) + (float(self.social_xp[other]) / (400.0))) * 1.2
        elif self.isFriend(other):
            nature = "good"
            proba = (1 / diff_kind) + (float(self.social_xp[other]) / (400.0))
        elif self.isEnnemy(other):
            nature = "bad"
            proba = (1 - ((1 / diff_kind)) - (float(self.social_xp[other]) / (400.0)))
        elif self.isSwornEnnemy(other):
            nature = "bad"
            proba = ((1 - (1 / diff_kind)) - (float(self.social_xp[other]) / (400.0))) * 1.2
        else:
            nature = "neutral"
            proba = 0.5 + (float(self.social_xp[other]) / (400.0))

        return {"p_interact_base": proba, "nature": nature}

    def shareFoodMemory(self, other):
        if self.known_food:
            self.last_social_interaction = "share food with {}".format(other.name)
            other.last_social_interaction = "food shared by {}".format(self.name)
            for mf in self.known_food.keys():    
                other.known_food[mf] = 0
            #add xp
            self.social_xp[other] = min((self.social_xp[other] + 3) * other.social, 100)
            other.social_xp[self] = min((other.social_xp[self] + 5) * self.social, 100)

            self.global_xp += 2

            pc.add_relation_sprite(self, other, "share food", basic_colors.LIME)
        else:
            self.befriend(other)

    def insult(self, other):
        #Change xp
        self.last_social_interaction = "insult {}".format(other.name)
        other.last_social_interaction = "insulted by {}".format(self.name)

        self.social_xp[other] = max((self.social_xp[other] - 3) * other.social, -100)
        other.social_xp[self] = max((other.social_xp[self] - 5) * self.social, -100)

        self.global_xp += 2

        pc.add_relation_sprite(self, other, "insult", basic_colors.RED)



    def befriend(self, other):
        self.last_social_interaction = "befriend {}".format(other.name)
        other.last_social_interaction = "befriended by {}".format(self.name)

        self.social_xp[other] = min((self.social_xp[other] + 2) * other.social, 100)
        other.social_xp[self] = min((other.social_xp[self] + 2) * self.social, 100)

        self.global_xp += 1

        pc.add_relation_sprite(self, other, "befriend", basic_colors.LIME)



    def snub(self, other):
        self.last_social_interaction = "sbun {}".format(other.name)
        other.last_social_interaction = "snubed by {}".format(self.name)

        self.social_xp[other] = min((self.social_xp[other] - 2) * other.social, 100)
        other.social_xp[self] = min((other.social_xp[self] - 2) * self.social, 100)

        self.global_xp += 1

        pc.add_relation_sprite(self, other, "snub", basic_colors.RED)


    def attack_other(self, other):
        self.social_xp[other] = min((self.social_xp[other] - 10) * other.social, 100)
        other.social_xp[self] = min((other.social_xp[self] - 10) * self.social, 100)

        atck_value = random.randint(1, 20) + self.attack
        if atck_value >= other.defense:
            damage_value = self.attack_damage
            for i in range(self.attack_dice[0]):
                damage_value += random.randint(1, self.attack_dice[1])

            other.hitpoint -= damage_value

            self.global_xp += 8

            self.last_social_interaction = "attack {} for {} dmg! ".format(other.name, damage_value)
            other.last_social_interaction = "attacked by {}, took {} dmg!".format(self.name, damage_value)

            pc.add_relation_sprite(self, other, "attack succeeds", basic_colors.RED)

        else:
            self.last_social_interaction = "attack {}: failed! ".format(other.name)
            other.last_social_interaction = "attacked by {}, defended!".format(self.name)

            other.global_xp += 8

            pc.add_relation_sprite(self, other, "attack failed", basic_colors.RED)


    def setNeigh_computation_thread(self, NCT):
        self.neigh_computation_thread = NCT

    def setClosestfood_computation_thread(self, CFCT):
        self.closestfood_computation_thread = CFCT

    def init(self):
        self._ticker = utils.perpetualTimer(1, self.tick)
        self._ticker.start()

    def isFriend(self, other):
        return float(abs(self.kindness - other.kindness)) <= 4 or self.social_xp[other] >= 50

    def isGoodFriend(self, other):
        return self.social_xp[other] >= 75

    def isEnnemy(self, other):
        return float(abs(self.kindness - other.kindness)) >= 6 or self.social_xp[other] <= -50

    def isSwornEnnemy(self, other):
        return self.social_xp[other] <= -75

    def computeNeighbours(self):
        self.neighbours = self.neigh_computation_thread.neighbours[self]

    def socialInteraction(self, other):
        interact = self.getInteractionProbability(other)

        # if utils.distance2p(self.getPose(), other.getPose()) < self.attack_range and (interact["nature"] == "bad" or self.isSwornEnnemy(other)) and random.random() <= self.getAttackProbability():
        if (interact["nature"] == "bad" or self.isSwornEnnemy(other)) and random.random() <= self.getAttackProbability():
            self.will_attack = True
            self.attack_target = other

        # elif self.isGoodFriend(other):
        #     if random.random() < interact["p_interact_base"]:
        #         self.shareFoodMemory(other)
        #     else:
        #         self.befriend(other)
        elif interact["nature"] == "good":
            if random.random() < interact["p_interact_base"]:
                self.shareFoodMemory(other)
            else:
                self.befriend(other)
        elif interact["nature"] == "neutral":
            if random.random() < interact["p_interact_base"]:
                self.snub(other)
            else:
                self.befriend(other)
        elif interact["nature"] == "bad":
            if random.random() < interact["p_interact_base"]:
                self.insult(other)
            else:
                self.snub(other)
        # elif self.isSwornEnnemy(other):
        #     if random.random() < interact["p_interact_base"]:
        #         self.insult(other)
        #     else:
        #         self.snub(other)

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

    def tick(self):
        if self.global_xp >= self.global_xp_next_lvl:
            self.level_up()

        self.social_cooldown = max(self.social_cooldown - 1, 0)

        self.updateFoodMemory() 
        if self._tick%10 == 0:
            self.env.pgo_obj.updatePosition(self)

            self.computeNeighbours()
            self.computeKnownFood()

        if self.hunger <= self.hunger_max*0.1:
            self.have_to_eat = False
        elif self.hungry():
            self.have_to_eat = True

        if self._tick%50 == 0:
            self.hunger += round((random.random() * 0.25) + 0.25, 2)
        if self.hunger >= self.hunger_max \
            or self.hitpoint <= 0:
            self.die()

        # if self._tick%200 == 0:
        #     self.socialInteraction()

        self._tick += 1
        if self._tick%1000 == 0:
            self._tick = 0

    def collectRessource(self, res):
        v = res.getSome(random.randint(15, 25))
        return v 

    def putInBagpack(self, res, qtt):
        if not res.name in self.bagpack.keys():
            self.bagpack[res.name] = 0
        self.bagpack[res.name] = round(qtt * self.harvester, 2)

    def haveFood(self):
        return "food" in self.bagpack.keys() and self.bagpack["food"] > 0

    def consumeFood(self):
        consume = 0
        if self.haveFood():
            consume = 1 if self.bagpack["food"] >= 1 else self.bagpack["food"]
            self.hunger -= consume
            self.bagpack["food"] -= consume
        if self.hunger <= 0:
            self.hunger = 0
        return consume

    def setIdleBehaviour(self):
        self.pause()
        if self.behaviour!= None and self.behaviour.state == "idle":
            return
        # self.behaviour = None
        self.behaviour = behaviour.IdleBehaviour(self, self.env)
        self.behaviour.computePath()
        self.resume()

    def setGOTOBehaviour(self, st):
        self.pause()
        # self.behaviour = None
        self.behaviour = behaviour.GOTOBehaviour(self, self.env, st)
        cp = self.behaviour.computePath()
        self.resume()


    def setGOTORessource(self, res):
        self.pause()
        # self.behaviour = None
        self.behaviour = behaviour.GOTORessource(self, self.env, res)
        cp = self.behaviour.computePath()
        self.resume()

    def setHarvestBehaviour(self, res):
        self.pause()
        # self.behaviour = None
        self.behaviour = behaviour.Harvest(self, self.env, res)
        self.behaviour.computePath()
        self.resume()

    def setWaitBehaviour(self, time):
        self.pause()
        # self.behaviour = None
        self.behaviour = behaviour.Wait(self, self.env, time)
        self.behaviour.computePath()
        self.resume()

    def setEmptyBehaviour(self):
        self.pause()
        # self.behaviour = None
        self.behaviour = behaviour.EmptyBehaviour(self, self.env)
        self.resume()

    def setRandomPose(self, maxx, maxy):
        super(NPC, self).setRandomPose(maxx, maxy)
        while self.env.collideOneObstacle_Point(self.getPose()):
            super(NPC, self).setRandomPose(maxx, maxy)
            
    def setCollectFoodBehaviour(self):
        self.pause()
        # self.behaviour = None
        self.behaviour = behaviour.CollectFood(self, self.env)
        self.resume()

    def setAttackBehaviour(self, te):
        self.pause()
        self.behaviour = behaviour.AttackBehaviour(self, self.env, te)
        self.behaviour.computePath()
        self.resume()

    def setConsumeFoodBehaviour(self):
        self.pause()
        self.behaviour = behaviour.ConsumeFood(self, self.env)
        self.resume()

    def setSocialInteractionBehaviour(self, other):
        self.pause()
        self.behaviour = behaviour.SocialInteraction(self, self.env, other)
        self.social_cooldown = self.behaviour.cooldown
        self.resume()

    def setDefaultBehaviour(self):
        if self.social_cooldown <= 0 and self.neighbours:
            l = [x for x in self.neighbours if utils.distance2p(self.getPose(), x.getPose()) < self.interaction_range]
            if l:
                other = random.choice(l)
                self.setSocialInteractionBehaviour(other)
            else:
                self.setIdleBehaviour()
        else:
            self.setIdleBehaviour()

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

        if self.have_to_eat and (self.behaviour.state != "wait" if self.behaviour != None else True):
            if self.haveFood():
                # cons = self.consumeFood()
                # self.setWaitBehaviour(int(round(cons))+1)
                self.setConsumeFoodBehaviour()
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

        if self.will_attack and self.attack_target != None:
            self.setAttackBehaviour(self.attack_target)
            self.will_attack = False
            self.attack_target = None

        # print(self.name, "update", self.behaviour.state)
        if self.behaviour != None and self.behaviour.state != "empty" and self.behaviour.state != "nothing":
            ns = self.behaviour.nextStep()
            # print ns
            if ns == -1:
                self.setDefaultBehaviour()
            elif ((self.behaviour.label == "GT" 
                        or self.behaviour.label == "W" 
                        or self.behaviour.label == "COFO"
                        or self.behaviour.label == "EAT"
                        or self.behaviour.label == "SOCINT"
                        or self.behaviour.label == "EAT"
                        or self.behaviour.label == "ATCK")
                        and ns == 1):
                self.setDefaultBehaviour()     
            elif self.behaviour.label == "I" and ns == 1:
                self.setWaitBehaviour(50)
        else:
            self.setDefaultBehaviour()
 
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

        self.time_per_unit = 4

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

    def getSome(self, qtt):
        v = round(qtt, 2) 
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