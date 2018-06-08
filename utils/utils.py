import math
import threading

class Pose(object):
    """docstring for Pose"""
    def __init__(self, nx, ny):
        self.x = nx
        self.y = ny

    def setPose(self, nx, ny):
        self.x = nx
        self.y = ny

    def getPose(self):
        return (self.x, self.y)
        
def getSign(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0

def closeEnough(a, b, _thresh=10):
    return abs(a-b) <= _thresh

def near(a, target, _thresh=10):
    return (a[0] > (target[0] - _thresh) and a[0] < (target[0] + _thresh)) and (a[1] > (target[1] - _thresh) and a[1] <(target[1] + _thresh))

def distance2p(a,b):
    return math.sqrt((a[0]-b[0])**2+(a[1]-b[1])**2)

class perpetualTimer():
    def __init__(self,t,hFunction):
        self.t=t
        self.hFunction = hFunction
        self.thread = threading.Timer(self.t, self.handle_function)

    def handle_function(self):
        self.hFunction()
        self.thread = threading.Timer(self.t, self.handle_function)
        self.thread.start()

    def start(self):
        self.thread.start()

    def cancel(self):
        self.thread.cancel()
