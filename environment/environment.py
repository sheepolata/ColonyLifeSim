import pygame
import math
import random 
import copy

import numpy as np

import utils.utils as utils
import utils.pathfinding as pf

class Environment(object):
    """docstring for Environment"""
    def __init__(self, w, h):
        self.width = w
        self.height = h

        self.obstacles = []
        self.ressources = {}

        self.min_tile_w = int(self.width*0.1)
        self.min_tile_h = int(self.height*0.1)

        self.graph_rect = []
        self.graph = {}
        self.graph_cost = {}

        self.river_path = []
        self.saved_rect_from_river = []

        self.loading = 0

    def addObstacle(self, obs):
        self.obstacles.append(obs)

    def addRessource(self, res):
        if not res.name in self.ressources.keys():
            self.ressources[res.name] = []
        self.ressources[res.name].append(res)

    def getClosestRessource(self, pose, resname):
        if not resname in self.ressources.keys() or not self.ressources[resname]:
            return None, None
        
        # result = self.ressources[resname][0]
        mini = float("inf")
        ok = None
        rect_ok = None
        for cand in [x for x in self.ressources[resname] if (x.harvestable and not x.used)]:
            # dist = utils.distance2p(pose, cand.getPose())
            cand_rect = self.getCurrentRect(cand.getPose())
            current_pose = self.getCurrentRect(pose)
            if current_pose == None or cand_rect == None:
                continue
            dist = pf.getPathLength(self, current_pose.center, cand_rect.center)
            if dist == -1:
                continue
            if dist <= mini:
                ok = cand
                rect_ok = cand_rect
                mini = dist
        return ok, rect_ok

    def getRandomValidPose(self):
        mini = 0
        maxi_h = self.height
        maxi_w = self.width

        tx = random.randint(mini, maxi_w)
        ty = random.randint(mini, maxi_h)
        while self.getCurrentRect((tx, ty)) == None:
            tx = random.randint(mini, maxi_w)
            ty = random.randint(mini, maxi_h)

        return (tx, ty)

    def collideOneObstacle_Point(self, point):
        for o in self.obstacles:
            if o.sprite.rect.collidepoint(point):
                return True
        for oriver in self.saved_rect_from_river:
            if oriver.collidepoint(point):
                return True
        return False

    def collideOneObstacle_Rect(self, rect):
        for o in self.obstacles:
            if o.sprite.rect.colliderect(rect):
                # print(rect, "collide", o.sprite.rect)
                return True
        return False

    def getRange(self, i, j, step):
        if i > j:
            return range(j, i, step)
        else:
            return range(i, j, step)

    def lineCollideObstacle(self, p1, p2):
        a = [p1[0], p1[1]]
        b = [p2[0], p2[1]]

        coefficients = np.polyfit(a, b, 1)

        for x in self.getRange(p1[0], p2[0], 1):
            y = coefficients[0] * x + coefficients[1]
            if self.collideOneObstacle_Point((x, y)):
                return True
        return False

    def constructRiver(self, nb_passage):
        print("constructRiver")
        paths = []

        prev_point = None


        wprange = range(10, self.width, self.width/5 - 1)
        wprange.append(self.width - 5)

        for i in range(1, len(wprange)):
            if prev_point == None:
                width_wp_left = wprange[i-1]

                height_left = random.randint(10, self.height - 10)
                
                first_point = self.getCurrentRect((width_wp_left, height_left))
                while first_point == None:
                    height_left = random.randint(10, self.height - 10)
                    first_point = self.getCurrentRect((width_wp_left, height_left))
            else:
                first_point = prev_point

            width_wp_rigth = wprange[i]
            height_right = random.randint(10, self.height - 10)
            second_point = self.getCurrentRect((width_wp_rigth, height_right))
            while second_point == None:
                height_right = random.randint(10, self.height - 10)
                second_point = self.getCurrentRect((width_wp_rigth, height_right))
            prev_point = second_point


            paths.append(pf.astar(second_point.center, first_point.center, self))

        for p in paths:
            for wp in p:
                self.river_path.append(wp)

        chosen = []
        for i in range(nb_passage):
            chosen.append(random.choice(self.river_path))

        # print chosen

        to_rm = [x for x in self.river_path if not x in chosen]
        for r in to_rm:
            self.saved_rect_from_river.append(copy.copy(self.getCurrentRect(r)))

        self.graph_rect = [x for x in self.graph_rect if not x.center in to_rm]

        for rm in to_rm:
            self.graph.pop(rm, None)
                
        self.constructGraph(areNeigbhoursInflated)

        print("End constructRiver")

    def getCurrentRect(self, point):
            for r in self.graph_rect:
                if r.collidepoint(point):
                    return r
            return None

    def splitEnvironment(self):
        print("split")
        self.graph_rect = []

        min_split_w = int(self.width*0.01)
        min_split_h = int(self.height*0.01)

        processList = []
        first = pygame.Rect((0, 0), (self.width, self.height))

        processList.append(first)

        lap = 0

        while processList:
            current = processList.pop()
            
            lap += 1

            self.graph[(current.left, current.top)] = []

            if((self.collideOneObstacle_Rect(current) and (current.width >= min_split_w or current.height >= min_split_h))):
                #split & add to process list
                new_rects = splitRect(current)

                for nr in new_rects:
                    processList.append(nr)

            elif((current.width > self.min_tile_w or current.height > self.min_tile_h)):
                #split & add to process list
                new_rects = splitRect(current, _correction=0)

                for nr in new_rects:
                    processList.append(nr)


            else:
                #add to final list
                self.graph_rect.append(current)

        print("Compute & remove  useless")
        self.graph_rect = [x for x in self.graph_rect if not self.collideOneObstacle_Rect(x)]
        print("end split")

    def constructGraph(self, neighbour_function):
        print("constructGraph")
        print("set costs")
        for r in self.graph_rect:
            self.graph_cost[r.center] = 1.0
        print("Compute neighbours")
        tot = len(self.graph_rect)
        curr = 0
        for r in self.graph_rect:
            curr += 1
            self.loading = round((float(curr)/float(tot))*100, 2)
            if self.loading % 4 == 0:
                print(str(self.loading) + "% (" + str(curr) + "/" + str(tot) + ")")

            self.graph[r.center] = {}
            for other in filter(lambda x :x.center != r.center and neighbour_function(r, x), self.graph_rect):
                self.graph[r.center][other.center] = utils.distance2p(r.center, other.center) * self.graph_cost[other.center]
        print("constructGraph end")

def splitRect(rect2split, _correction=0):
    nwf = rect2split.width/2.0
    nhf = rect2split.height/2.0
    
    nw = int(round(nwf))
    nh = int(round(nhf))

    r1 = pygame.Rect((rect2split.left, rect2split.top), (nw, nh))

    r2 = pygame.Rect((rect2split.left + nw, rect2split.top), (nw+_correction, nh))

    r3 = pygame.Rect((rect2split.left, rect2split.top + nh), (nw, nh))

    r4 = pygame.Rect((rect2split.left + nw, rect2split.top + nh), (nw+_correction, nh))

    return [r1, r2, r3, r4]

def areNeigbhoursSquare(rect1, rect2):
    # return (
    #     rect1.top == rect2.top + rect2.height
    #     or rect1.top + rect1.height == rect2.top
    #     or rect1.left == rect2.left + rect2.width
    #     or rect1.left + rect1.width == rect2.left
    #     )
    return (
        (utils.closeEnough(rect1.top, rect2.top + rect2.height, _thresh=5) and rect1.left == rect2.left)
        or (utils.closeEnough(rect1.top + rect1.height, rect2.top, _thresh=5) and rect1.left == rect2.left)
        or (utils.closeEnough(rect1.left, rect2.left + rect2.width, _thresh=5) and rect1.top == rect2.top)
        or (utils.closeEnough(rect1.left + rect1.width, rect2.left, _thresh=5) and rect1.top == rect2.top)
        )



def areNeigbhoursInflated(rect1, rect2):
    return rect1.inflate(1, 1).colliderect(rect2.inflate(1, 1))