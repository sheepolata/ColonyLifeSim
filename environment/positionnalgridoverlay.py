import environment as Env
import utils.utils as utils
import utils.geometry as geo
import utils.pathfinding as pf
import pygame

class PositionnalGridOverlay(object):
    def __init__(self, env, gridsize):
        super(PositionnalGridOverlay, self).__init__()
        self.env = env

        self.gridsize = gridsize
        self.grid = []


        self.positions = {}
        self.rectContainsNPC = {}

        self.rectContainsFood = {}

        for w in range(0, self.env.width, int(round(self.env.width / self.gridsize))):
            self.grid.append([])
            i = 0
            for h in range(0, self.env.height, int(round(self.env.height / self.gridsize))):
                self.grid[0].append(pygame.Rect((w, h), (int(round(self.env.width / self.gridsize)), int(round(self.env.height / self.gridsize)))))
                i += 1

        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                self.rectContainsNPC[self.grid[i][j].center] = []

        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                self.rectContainsFood[self.grid[i][j].center] = []

    def updateRemoveDead(self):
        for k in self.rectContainsNPC:
            self.rectContainsNPC[k] = [x for x in self.rectContainsNPC[k] if not x.dead]

    def updateFoodPosition(self, food):
        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                if self.grid[i][j].collidepoint(food.getPose()):
                    self.positions[food] = self.grid[i][j]
                    if not food in self.rectContainsFood[self.grid[i][j].center] : self.rectContainsFood[self.grid[i][j].center].append(food)
                elif food in self.rectContainsFood[self.grid[i][j].center] : self.rectContainsFood[self.grid[i][j].center].remove(food)


    def updatePosition(self, npc):
        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                if self.grid[i][j].collidepoint(npc.getPose()):
                    self.positions[npc] = self.grid[i][j]
                    if not npc in self.rectContainsNPC[self.grid[i][j].center] : self.rectContainsNPC[self.grid[i][j].center].append(npc)
                elif npc in self.rectContainsNPC[self.grid[i][j].center] : self.rectContainsNPC[self.grid[i][j].center].remove(npc)

    def updateAllPosition(self):
        for n in self.env.npcs:
            self.updatePosition(n)

    def getRectInRangeStrict(self, npc):
        res = []
        for lt in self.grid:
            for t in lt:
                asser, p = geo.circleContainsRect(npc.getPose(), npc.vision_radius, t)
                if asser :#and not pf.checkStraightPath(self.env, npc.getPose(), p, 5, check_river=False):
                    res.append(t)
        return res

    def getRectInRangeLimit(self, npc):
        res = []
        for lt in self.grid:
            for t in lt:
                if geo.circleIntersectRect(npc.getPose(), npc.vision_radius, t):
                    res.append(t)
        return res

    def getTileInRange(self, npc):
        pass