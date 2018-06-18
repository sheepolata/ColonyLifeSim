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

# GCD and LCM are not in math module.  They are in gmpy, but these are simple enough:
def gcd(a,b):
    """Compute the greatest common divisor of a and b"""
    while b > 0:
        a, b = b, a % b
    return a
    
def lcm(a, b):
    """Compute the lowest common multiple of a and b"""
    return a * b / gcd(a, b)