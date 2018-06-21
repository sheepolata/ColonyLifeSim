import threading
import utils.pathfinding as pf
import utils.utils as utils
import time

from joblib import Parallel, delayed
import multiprocessing


class NeighboursComputationThread(threading.Thread):
    def __init__(self, env):
        super(NeighboursComputationThread, self).__init__()
        self.daemon = True
        self.running = True

        self.env = env

        self.name = "NCT"

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
            # t=time.time()
            self.computeNeighbours()
            # print(time.time() - t)

    def computeNeighbours(self):
        for focus in self.env.npcs:
            if not focus in self.neighbours.keys(): self.neighbours[focus] = []
            rects = self.env.pgo_obj.getRectInRangeStrict(focus)
            focus.neighbours_rect = rects
            
            # rectslimit = self.env.pgo_obj.getRectInRangeLimit(focus)
            # rects.extend(rectslimit)

            res = []
            for r in rects:
                res.extend(self.env.pgo_obj.rectContainsNPC[r.center])
            # for r in rectslimit:
            #     for n in self.env.pgo_obj.rectContainsNPC[r.center]:
            #         if utils.distance2p(focus.getPose(), n.getPose()) <= focus.vision_radius: res.append(n)
            self.neighbours[focus] = [x for x in res if not pf.checkStraightPath(self.env, focus.getPose(), x.getPose(), 10, check_river=False)]

            # for npc in self.env.npcs:
            #     if npc == focus: continue

            #     if not pf.checkStraightPath(self.env, focus.getPose(), npc.getPose(), 10, check_river=False) and utils.distance2p(focus.getPose(), npc.getPose()) <= focus.vision_radius:
            #         if not npc in self.neighbours[focus]:
            #             self.neighbours[focus].append(npc)
            #     elif npc in self.neighbours[focus]:
            #         self.neighbours[focus].remove(npc)
            # inloop_op_NCT(focus, self)

        #multiprocessing solution : not working
        # pool = multiprocessing.Pool(multiprocessing.cpu_count())
        # zip(*pool.map(inloop_op_NCT, [focus for focus in self.env.npcs], self))

        #Joblib solution : not good in multithreading
        # num_cores = multiprocessing.cpu_count()
        # Parallel(n_jobs=num_cores)(delayed(inloop_op_NCT)(focus, self) for focus in self.env.npcs)
     
# def inloop_op_NCT(focus, ct):
#     if not focus in ct.neighbours.keys(): ct.neighbours[focus] = []
#     for npc in ct.env.npcs:
#         if npc == focus: continue

#         if not pf.checkStraightPath(ct.env, focus.getPose(), npc.getPose(), 10, check_river=False) and utils.distance2p(focus.getPose(), npc.getPose()) <= focus.vision_radius:
#             if not npc in ct.neighbours[focus]:
#                 ct.neighbours[focus].append(npc)
#         elif npc in ct.neighbours[focus]:
#             ct.neighbours[focus].remove(npc)

class ClosestFoodComputationThread(threading.Thread):
    def __init__(self, env):
        super(ClosestFoodComputationThread, self).__init__()
        self.daemon = True

        self.env = env
        self.running = True

        self.name = "CFCT"

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

            # if not focus in self.closestFood.keys(): self.closestFood[focus] = []
            # rects = self.env.pgo_obj.getRectInRangeStrict(focus)
            # res = []
            # for r in rects:
            #     res.extend(self.env.pgo_obj.rectContainsFood[r.center])
            # self.closestFood[focus] = res

            if not focus in self.closestFood.keys(): self.closestFood[focus] = []
            for f in self.env.ressources["food"]:
                if not pf.checkStraightPath(self.env, focus.getPose(), f.getPose(), 10, check_river=False) and utils.distance2p(focus.getPose(), f.getPose()) <= focus.vision_radius:
                    if not f in self.closestFood[focus]:
                        self.closestFood[focus].append(f)
                elif f in self.closestFood[focus]:
                    self.closestFood[focus].remove(f)
            
            # inloop_op_CFCT(focus, self)

    def run(self):
        while self.running:
            self.computeClosestFood()

def inloop_op_CFCT(focus, ct):
    for f in ct.env.ressources["food"]:
        if not focus in ct.closestFood.keys(): ct.closestFood[focus] = []

        if not pf.checkStraightPath(ct.env, focus.getPose(), f.getPose(), 10, check_river=False) and utils.distance2p(focus.getPose(), f.getPose()) <= focus.vision_radius:
            if not f in ct.closestFood[focus]:
                ct.closestFood[focus].append(f)
        elif f in ct.closestFood[focus]:
            ct.closestFood[focus].remove(f)