import pygame
import math

import numpy as np

import utils.utils as utils

class Environment(object):
    """docstring for Environment"""
    def __init__(self, w, h):
        self.width = w
        self.height = h

        self.obstacles = []

        self.min_tile_w = int(self.width*0.05)
        self.min_tile_h = int(self.height*0.05)
        self.graph_rect = []
        self.graph = {}
        self.graph_cost = {}

        self.loading = 0

    def addObstacle(self, obs):
        self.obstacles.append(obs)
        # self.splitEnvironment()
        # self.constructGraph()


    def collideOneObstacle_Point(self, point):
        for o in self.obstacles:
            if o.sprite.rect.collidepoint(point):
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

        # self.graph[first] = None

        lap = 0

        while processList:
            # print("passage", len(processList))
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

        # print("Compute useless")
        # to_rm = []
        # for r in self.graph_rect:
        #     if self.collideOneObstacle_Rect(r):
        #         to_rm.append(r)
        
        # print("Remove useless")
        # self.graph_rect = [x for x in self.graph_rect if x not in to_rm]

        # for item in to_rm:
        #     while self.graph_rect.count(item) > 0:
        #         self.graph_rect.remove(item)

        print("end split")

    def constructGraph(self):
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
            for other in filter(lambda x :x.center != r.center and areNeigbhours(r, x), self.graph_rect):
                self.graph[r.center][other.center] = utils.distance2p(r.center, other.center) * self.graph_cost[other.center]
        print("constructGraph end")

def splitRect(rect2split, _correction=0):
    nw = math.floor(rect2split.width/2) 
    nh = math.floor(rect2split.height/2)

    r1 = pygame.Rect((rect2split.left, rect2split.top), (nw, nh))

    r2 = pygame.Rect((rect2split.left + nw, rect2split.top), (nw+_correction, nh))

    r3 = pygame.Rect((rect2split.left, rect2split.top + nh), (nw, nh))

    r4 = pygame.Rect((rect2split.left + nw, rect2split.top + nh), (nw+_correction, nh))

    return [r1, r2, r3, r4]

def areNeigbhours(rect1, rect2):
    return rect1.inflate(15, 15).colliderect(rect2.inflate(15, 15))