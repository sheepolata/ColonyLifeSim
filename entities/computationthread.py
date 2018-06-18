import threading
import utils.pathfinding as pf
import utils.utils as utils

class NeighboursComputationThread(threading.Thread):
    def __init__(self, env):
        super(NeighboursComputationThread, self).__init__()
        self.daemon = True
        self.running = True

        self.env = env

        self.neighbours = {}
        for focus in self.env.npcs:
            self.neighbours[focus] = []

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

    def join(self, timeout):
        print("NCT join")
        super(NeighboursComputationThread, self).join(timeout)

    def run(self):
        while self.running:
            self.computeNeighbours()

    def computeNeighbours(self):
        for focus in self.env.npcs:
            if not focus in self.neighbours.keys(): self.neighbours[focus] = []
            for npc in self.env.npcs:
                if npc == focus: continue

                if not pf.checkStraightPath(self.env, focus.getPose(), npc.getPose(), 10, check_river=False) and utils.distance2p(focus.getPose(), npc.getPose()) <= focus.vision_radius:
                    if not npc in self.neighbours[focus]:
                        self.neighbours[focus].append(npc)
                elif npc in self.neighbours[focus]:
                    self.neighbours[focus].remove(npc)
        
class ClosestFoodComputationThread(threading.Thread):
    def __init__(self, env):
        super(ClosestFoodComputationThread, self).__init__()
        self.daemon = True

        self.env = env
        self.running = True

        self.closestFood = {}
        for focus in env.npcs:
            self.closestFood[focus] = []

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

    def join(self, timeout):
        print("CFCT join")
        super(ClosestFoodComputationThread, self).join(timeout)

    def computeClosestFood(self):
        for focus in self.env.npcs:
            if not focus in self.closestFood.keys(): self.closestFood[focus] = []
            for f in self.env.ressources["food"]:
                if not pf.checkStraightPath(self.env, focus.getPose(), f.getPose(), 10, check_river=False) and utils.distance2p(focus.getPose(), f.getPose()) <= focus.vision_radius:
                    if not f in self.closestFood[focus]:
                        self.closestFood[focus].append(f)
                elif f in self.closestFood[focus]:
                    self.closestFood[focus].remove(f)

    def run(self):
        while self.running:
            self.computeClosestFood()