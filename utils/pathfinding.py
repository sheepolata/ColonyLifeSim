import geometry as geo
import time
import utils

#_start and _goal here are Coordinates
def heuristic_cost_estimate(_current, _goal):
    # res = 10 * (abs(_current[0] - _goal[0]) + abs(_current[1] - _goal[1]))
    res = utils.distance2p(_current, _goal)
    return res

def astar(_start, _goal, env):
    # The set of nodes already evaluated
    closedSet = []

    # The set of currently discovered nodes that are not evaluated yet.
    # Initially, only the start node is known.
    openSet = [_start]

    # For each node, which node it can most efficiently be reached from.
    # If a node can be reached from many nodes, cameFrom will eventually contain the
    # most efficient previous step.
    came_from = {}

    # For each node, the cost of getting from the start node to that node.

    g_score = {}
    for i in env.graph.keys():
        g_score[i] = float("inf")
    
    # The cost of going from start to start is zero.
    g_score[_start] = 0.0

    # For each node, the total cost of getting from the start node to the goal
    # by passing by that node. That value is partly known, partly heuristic.
    f_score = {}
    for i in env.graph.keys():
        f_score[i] = float("inf")
    f_score[_start] = heuristic_cost_estimate(_start, _goal)

    while openSet:

        #current = Node in openSet with the lowest f_score
        mini = float("inf")
        current = None
        for elt in openSet:
            if mini >= f_score[elt]:
                mini = f_score[elt]
                current = elt

        if current == None:
            print("Error : current == None")
            return []

        if current == _goal:
            return reconstructPath(came_from, current)

        openSet.remove(current)
        closedSet.append(current)

        #For each neighbours of current
        for _neighbour in env.graph[current]:
            if _neighbour in closedSet:
                continue

            if _neighbour not in openSet:
                openSet.append(_neighbour)

            #The distance from start to a neighbor
            #the "dist_between" function may vary as per the solution requirements.
            tentative_gScore = g_score[current] + env.graph[current][_neighbour]
            if tentative_gScore >= g_score[_neighbour]:
                continue

            came_from[_neighbour] = current
            g_score[_neighbour] = tentative_gScore
            f_score[_neighbour] = g_score[_neighbour] + heuristic_cost_estimate(_neighbour, _goal)

    return None


def reconstructPath(came_from, current):
    total_path = [current]
    while current in came_from.keys():
        current = came_from[current]
        total_path.append(current)

    return total_path #+ [total_path[-1]]

def computePathLength(env, path):
    if not path:
        return -1
    if len(path) == 1:
        return 0
    res = env.graph[path[0]][path[1]]
    for i in range(1, len(path) - 1):
        res = res + env.graph[path[i]][path[i+1]]
    return res

def getPathLength(env, pose1, pose2, approx=False):
    #NEW BUT NOT GOOD
    # astar_needed = checkStraightPath(env, pose1, pose2, 2)
    # if astar_needed:
    #     path = astar(pose1, pose2, env)
    #     res = computePathLength(env, path)
    # else:
    #     res = utils.distance2p(pose1, pose2)
    if approx:
        res = utils.distance2p(pose1, pose2)
    #OLD
    else:
        path = astar(pose1, pose2, env)
        res = computePathLength(env, path)
    
    return res
    
    # return utils.distance2p(pose1, pose2)

def checkStraightPath(env, p1, p2, precision, check_obs=True, check_river=True):
    #if line from entity.pos to target is OK, do not compute astar
        #y = a*x + b => a==0 : parallele; a==inf : perpendicular; a == (-)1 : (-)45deg
    a, b = geo.computeLineEquation(p1, p2)
    astar_needed = False
    if a == None or b == None:
        astar_needed = True
    elif abs(p1[0] - p2[0]) > abs(p1[1] - p2[1]):
        mini = min(p1[0], p2[0])
        maxi = max(p1[0], p2[0])

        for step_x in range(int(mini), int(maxi), int(precision)):
            y = a*step_x + b
            if env.collideOneObstacle_Point((step_x, y), check_obs=check_obs, check_river=check_river):
                astar_needed = True
    else:
        mini = min(p1[1], p2[1])
        maxi = max(p1[1], p2[1])

        for step_y in range(int(mini), int(maxi), int(precision)):
            # y = a*step_x + b
            x = (step_y - b)/a
            if env.collideOneObstacle_Point((x, step_y), check_obs=check_obs, check_river=check_river):
                astar_needed = True

    return astar_needed